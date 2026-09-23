#!/usr/bin/env python3
"""Run the Chunky pre-generation campaign only while no players are online.

The controller polls `list` over RCON about once per second. With zero players
it starts or continues the current Chunky target; as soon as a player is seen it
pauses the task (`chunky pause <world>`). Start and continue are sent as
`execute unless entity @a run ...`, so the server checks again for players right
before running them; a blank reply means a player arrived and nothing ran.
Targets run one after another and the next target only starts after the current
one is verified as finished.

Campaign progress is kept in a JSON state file on a durable path. Chunky keeps
its own per-world progress in `config/chunky/tasks/`, so a paused task resumes
with `chunky continue <world>` after controller or server restarts. The
controller never runs `chunky cancel`, `chunky trim` or `chunky confirm`.

See docs/CHUNK_PREGEN.md for operation.
"""

import argparse
import fcntl
import json
import logging
import os
import re
import signal
import socket
import struct
import sys
import time
from pathlib import Path

# Generation order and radius (blocks, circle centered at 0 0).
TARGETS = (
    ("minecraft:the_nether", 1000),
    ("minecraft:overworld", 8000),
    ("minecraft:the_end", 8000),
)

STATE_VERSION = 1
DEFAULT_POLL_INTERVAL_SECONDS = 1.0
DEFAULT_RESUME_DELAY_SECONDS = 30.0
# A finished task is saved (cancelled=true) right after the finish message is
# logged. Allow this long for the log line to show up before failing.
COMPLETION_LOG_WAIT_SECONDS = 15.0
RCON_FAILURE_LOG_INTERVAL_SECONDS = 60.0

# Runs the wrapped command only if no player is online, checked by the server
# in the same tick. The reply is blank when a player was found.
IDLE_ONLY = "execute unless entity @a run "

FORMATTING_CODES = re.compile(r"\x1b\[[0-9;]*[A-Za-z]|§.")
PLAYER_LIST = re.compile(r"There are (\d+) of a max of (\d+) players online:")
TASK_RUNNING = re.compile(r"Task running for (\S+)\. Processed: ")

log = logging.getLogger("chunky-idle")


class ControllerError(Exception):
    """Unexpected server response or inconsistent campaign state."""


class RconError(Exception):
    """RCON connection could not be used (server down or restarting)."""


class RconAuthError(Exception):
    """RCON rejected the password."""


def strip_formatting(text):
    return FORMATTING_CODES.sub("", text).strip()


def parse_player_count(text):
    """Return the online player count from Minecraft `list` output.

    Raises ValueError when the text is not a recognizable `list` response, so an
    unexpected reply can never be mistaken for an empty server.
    """
    match = PLAYER_LIST.match(strip_formatting(text))
    if match is None:
        raise ValueError(f"unrecognized list response: {text!r}")
    return int(match.group(1))


def parse_running_worlds(text):
    """Return the worlds `chunky progress` reports as running.

    Raises ValueError when the text is neither `No tasks running.` nor a task
    progress report.
    """
    cleaned = strip_formatting(text)
    if cleaned == "[Chunky] No tasks running.":
        return set()
    worlds = set(TASK_RUNNING.findall(cleaned))
    if not worlds:
        raise ValueError(f"unrecognized chunky progress response: {text!r}")
    return worlds


class RconClient:
    """Minimal Source RCON client keeping one connection open between polls."""

    AUTH = 3
    COMMAND = 2
    AUTH_RESPONSE = 2

    def __init__(self, host, port, password, timeout=5.0):
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.sock = None
        self.next_id = 1

    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def command(self, text):
        try:
            if self.sock is None:
                self._connect()
            request_id = self._send(self.COMMAND, text)
            response_id, _, body = self._receive()
        except (OSError, EOFError) as error:
            self.close()
            raise RconError(f"RCON {self.host}:{self.port} failed: {error}") from error
        if response_id != request_id:
            self.close()
            raise RconError(f"RCON response id {response_id} does not match request {request_id}")
        return body

    def _connect(self):
        self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        request_id = self._send(self.AUTH, self.password)
        while True:
            response_id, packet_type, _ = self._receive()
            if packet_type == self.AUTH_RESPONSE:
                break
        if response_id == -1 or response_id != request_id:
            self.close()
            raise RconAuthError("RCON authentication failed; check RCON_PASSWORD")

    def _send(self, packet_type, body):
        request_id = self.next_id
        self.next_id += 1
        payload = struct.pack("<ii", request_id, packet_type) + body.encode("utf-8") + b"\x00\x00"
        self.sock.sendall(struct.pack("<i", len(payload)) + payload)
        return request_id

    def _receive(self):
        (length,) = struct.unpack("<i", self._read_exact(4))
        payload = self._read_exact(length)
        response_id, packet_type = struct.unpack("<ii", payload[:8])
        body = payload[8:-2].decode("utf-8", errors="replace")
        return response_id, packet_type, body

    def _read_exact(self, size):
        data = b""
        while len(data) < size:
            chunk = self.sock.recv(size - len(data))
            if not chunk:
                raise EOFError("connection closed by server")
            data += chunk
        return data


def read_task_file(chunky_dir, world):
    """Return Chunky's saved task properties for `world`, or None if absent."""
    path = Path(chunky_dir) / "tasks" / (world.replace(":", "/") + ".properties")
    if not path.exists():
        return None
    properties = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator:
            raise ControllerError(f"malformed line in {path}: {line!r}")
        properties[key.strip()] = value.strip()
    return properties


def task_matches_target(task, world, radius):
    try:
        return (
            task.get("world") == world
            and task.get("shape") == "circle"
            and float(task.get("center-x", "nan")) == 0.0
            and float(task.get("center-z", "nan")) == 0.0
            and float(task.get("radius", "nan")) == float(radius)
        )
    except ValueError as error:
        raise ControllerError(f"malformed Chunky task file for {world}: {task}") from error


def task_is_cancelled(task, world):
    value = task.get("cancelled")
    if value not in ("true", "false"):
        raise ControllerError(f"Chunky task file for {world} has cancelled={value!r}")
    return value == "true"


def log_marker(log_path):
    stat = os.stat(log_path)
    return {"inode": stat.st_ino, "offset": stat.st_size}


def finish_logged_since(log_path, marker, world):
    """Whether the server log shows the world's task finished after `marker`.

    Returns None when the log was rotated since the marker (server restarted),
    because the finish can then no longer be verified from latest.log.
    """
    stat = os.stat(log_path)
    if stat.st_ino != marker["inode"] or stat.st_size < marker["offset"]:
        return None
    with open(log_path, "rb") as log_file:
        log_file.seek(marker["offset"])
        text = log_file.read().decode("utf-8", errors="replace")
    finished = re.compile(
        r"\[Chunky\] Task finished for " + re.escape(world) + r"\. Processed: [\d,.]+ chunks \(100[.,]00%\)"
    )
    return finished.search(text) is not None


class CampaignState:
    """Durable campaign progress, written atomically to a JSON file."""

    def __init__(self, path):
        self.path = Path(path)
        self.completed = []
        self.active = None

    def load(self):
        if not self.path.exists():
            log.info("no state file at %s; starting a new campaign", self.path)
            self.save()
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if data.get("version") != STATE_VERSION:
            raise ControllerError(f"state file {self.path} has unsupported version {data.get('version')!r}")
        if [tuple(target) for target in data.get("targets", [])] != list(TARGETS):
            raise ControllerError(f"state file {self.path} targets {data.get('targets')} differ from {list(TARGETS)}")
        self.completed = data["completed"]
        self.active = data["active"]
        expected_completed = [world for world, _ in TARGETS[: len(self.completed)]]
        if self.completed != expected_completed:
            raise ControllerError(f"state file {self.path} completed list {self.completed} is out of order")
        target = self.current_target()
        if self.active is not None and (target is None or self.active["world"] != target[0]):
            raise ControllerError(f"state file {self.path} active target {self.active} is not the next target {target}")

    def save(self):
        data = {
            "version": STATE_VERSION,
            "targets": [list(target) for target in TARGETS],
            "completed": self.completed,
            "active": self.active,
        }
        temporary = self.path.with_suffix(".tmp")
        with open(temporary, "w", encoding="utf-8") as state_file:
            json.dump(data, state_file, indent=2)
            state_file.write("\n")
            state_file.flush()
            os.fsync(state_file.fileno())
        os.replace(temporary, self.path)

    def current_target(self):
        if len(self.completed) >= len(TARGETS):
            return None
        return TARGETS[len(self.completed)]


class Controller:
    def __init__(self, rcon, state, chunky_dir, server_log, resume_delay, clock=time.monotonic):
        self.rcon = rcon
        self.state = state
        self.chunky_dir = chunky_dir
        self.server_log = server_log
        self.resume_delay = resume_delay
        self.clock = clock
        # Whether this process has confirmed the active task is paused since it
        # last started or continued it. Unknown (False) after a restart.
        self.pause_confirmed = False
        self.last_player_seen = None
        self.unverified_finish_since = None

    def step(self):
        """Run one poll cycle. Returns False once every target is complete."""
        target = self.state.current_target()
        if target is None:
            return False
        world, radius = target

        players = parse_player_count(self.rcon.command("list"))
        if players > 0:
            self.last_player_seen = self.clock()
            if self.state.active is not None and not self.pause_confirmed:
                self.pause(world, reason=f"{players} player(s) online")
            return True

        if self.last_player_seen is not None and self.clock() - self.last_player_seen < self.resume_delay:
            return True

        running = parse_running_worlds(self.rcon.command("chunky progress"))
        unexpected = running - {world}
        if unexpected:
            raise ControllerError(f"Chunky is running tasks not owned by this campaign: {sorted(unexpected)}")
        if world in running:
            if self.state.active is None:
                raise ControllerError(f"Chunky is running {world} but the campaign never started it")
            self.pause_confirmed = False
            return True

        task = read_task_file(self.chunky_dir, world)
        if self.state.active is None:
            if task is not None and not task_is_cancelled(task, world):
                raise ControllerError(
                    f"a resumable Chunky task for {world} exists that this campaign did not start: {task}"
                )
            self.start(world, radius)
        elif task is not None and task_matches_target(task, world, radius):
            if task_is_cancelled(task, world):
                self.verify_completion(world)
            else:
                self.resume(world)
        elif self.state.active["phase"] == "starting":
            self.start(world, radius)
        else:
            raise ControllerError(f"Chunky task file for {world} no longer matches the started target: {task}")
        return True

    def player_arrived(self, action, world):
        self.last_player_seen = self.clock()
        log.info("did not %s %s: a player joined right before the command", action, world)

    def start(self, world, radius):
        previous = self.state.active
        self.state.active = {"world": world, "phase": "starting", "log_marker": log_marker(self.server_log)}
        self.state.save()
        command = f"{IDLE_ONLY}chunky start {world} circle 0 0 {radius}"
        response = strip_formatting(self.rcon.command(command))
        if not response:
            self.state.active = previous
            self.state.save()
            self.player_arrived("start", world)
            return
        if not response.startswith(f"[Chunky] Task started in {world} for the circle region"):
            raise ControllerError(f"`{command}` was not accepted: {response!r}")
        self.state.active["phase"] = "started"
        self.state.save()
        self.pause_confirmed = False
        log.info("started %s radius %s", world, radius)

    def resume(self, world):
        previous = dict(self.state.active)
        self.state.active["log_marker"] = log_marker(self.server_log)
        self.state.save()
        command = f"{IDLE_ONLY}chunky continue {world}"
        response = strip_formatting(self.rcon.command(command))
        if not response:
            self.state.active = previous
            self.state.save()
            self.player_arrived("continue", world)
            return
        if response != f"[Chunky] Task continuing for {world}.":
            raise ControllerError(f"`{command}` was not accepted: {response!r}")
        self.pause_confirmed = False
        log.info("continued %s (no players online)", world)

    def pause(self, world, reason):
        response = strip_formatting(self.rcon.command(f"chunky pause {world}"))
        if response == f"[Chunky] Task paused for {world}.":
            log.info("paused %s: %s", world, reason)
        elif response != "[Chunky] No tasks to pause.":
            raise ControllerError(f"`chunky pause {world}` returned an unexpected response: {response!r}")
        self.pause_confirmed = True

    def verify_completion(self, world):
        finished = finish_logged_since(self.server_log, self.state.active["log_marker"], world)
        if finished is None:
            raise ControllerError(
                f"Chunky saved {world} as ended, but {self.server_log} was rotated since the task last ran, "
                "so the finish cannot be verified. Check the rotated logs for "
                f"'[Chunky] Task finished for {world}' before resolving the state file manually."
            )
        if not finished:
            if self.unverified_finish_since is None:
                self.unverified_finish_since = self.clock()
            if self.clock() - self.unverified_finish_since < COMPLETION_LOG_WAIT_SECONDS:
                return
            raise ControllerError(
                f"Chunky saved {world} as ended but no 100% finish line was logged; "
                "the task may have been cancelled outside this controller."
            )
        self.unverified_finish_since = None
        self.state.completed.append(world)
        self.state.active = None
        self.state.save()
        log.info("completed %s", world)

    def pause_on_exit(self):
        """Pause the active task so generation never runs unsupervised."""
        if self.state.active is None:
            return
        world = self.state.active["world"]
        try:
            self.pause(world, reason="controller exiting")
        except (RconError, RconAuthError, ControllerError) as error:
            log.error("could not pause %s while exiting: %s", world, error)


def check_chunky_config(chunky_dir):
    config_path = Path(chunky_dir) / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("continueOnRestart") is not False:
        raise ControllerError(
            f"{config_path} must set continueOnRestart to false, otherwise Chunky resumes tasks on server start "
            "before the player check"
        )


def acquire_lock(state_path):
    lock_file = open(Path(state_path).with_suffix(".lock"), "w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise ControllerError(f"another controller already holds {lock_file.name}") from None
    return lock_file


def handle_sigterm(signum, frame):
    raise KeyboardInterrupt


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--state-file", default="/state/chunky_idle_state.json")
    parser.add_argument("--chunky-dir", default="/chunky", help="the server's config/chunky directory")
    parser.add_argument("--server-log", default="/server-logs/latest.log")
    parser.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL_SECONDS)
    parser.add_argument(
        "--resume-delay",
        type=float,
        default=DEFAULT_RESUME_DELAY_SECONDS,
        help="seconds without players, after a player was seen, before generation resumes",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    password = os.environ.get("RCON_PASSWORD")
    if not password:
        log.error("RCON_PASSWORD is not set")
        return 2
    rcon = RconClient(os.environ.get("RCON_HOST", "minecraft"), int(os.environ.get("RCON_PORT", "25575")), password)

    try:
        lock = acquire_lock(args.state_file)
        check_chunky_config(args.chunky_dir)
        state = CampaignState(args.state_file)
        state.load()
    except (ControllerError, OSError, ValueError) as error:
        log.error("%s", error)
        return 1

    controller = Controller(rcon, state, args.chunky_dir, args.server_log, args.resume_delay)
    log.info("campaign: completed=%s active=%s", state.completed, state.active)
    signal.signal(signal.SIGTERM, handle_sigterm)

    rcon_failing_since = None
    last_failure_log = None
    try:
        while True:
            cycle_started = time.monotonic()
            try:
                if not controller.step():
                    log.info("all targets complete: %s", [world for world, _ in TARGETS])
                    return 0
                if rcon_failing_since is not None:
                    log.info("RCON available again after %.0fs", time.monotonic() - rcon_failing_since)
                    rcon_failing_since = None
            except RconError as error:
                # Server stopped or restarting: take no action until it answers.
                controller.pause_confirmed = False
                now = time.monotonic()
                if rcon_failing_since is None:
                    rcon_failing_since = now
                    last_failure_log = now
                    log.error("%s; generation will not be started or continued until RCON answers", error)
                elif now - last_failure_log >= RCON_FAILURE_LOG_INTERVAL_SECONDS:
                    last_failure_log = now
                    log.error("RCON still failing after %.0fs: %s", now - rcon_failing_since, error)
            time.sleep(max(0.0, args.poll_interval - (time.monotonic() - cycle_started)))
    except (ControllerError, ValueError, RconAuthError, OSError) as error:
        log.error("stopping: %s", error)
        controller.pause_on_exit()
        return 1
    except KeyboardInterrupt:
        log.info("stop requested")
        controller.pause_on_exit()
        return 0
    finally:
        rcon.close()
        lock.close()


if __name__ == "__main__":
    sys.exit(main())
