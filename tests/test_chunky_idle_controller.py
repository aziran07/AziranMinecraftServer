"""Contract tests for the player-count gate used by Chunky pre-generation."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.chunky_idle_controller import (
    TARGETS,
    CampaignState,
    Controller,
    ControllerError,
    finish_logged_since,
    log_marker,
    parse_player_count,
    parse_running_worlds,
)


class FakeRcon:
    def __init__(self, responses):
        self.responses = responses
        self.commands = []

    def command(self, command):
        self.commands.append(command)
        return self.responses[command]


class PlayerCountTests(unittest.TestCase):
    def test_empty_server(self):
        self.assertEqual(
            parse_player_count("There are 0 of a max of 20 players online: \n\x1b[0m"),
            0,
        )

    def test_active_players(self):
        self.assertEqual(
            parse_player_count("There are 2 of a max of 20 players online: a, b\n"),
            2,
        )

    def test_malformed_response_is_an_error(self):
        with self.assertRaises(ValueError):
            parse_player_count("[Chunky] No tasks running.")

    def test_missing_response_is_an_error(self):
        with self.assertRaises(ValueError):
            parse_player_count("")


class TargetsTests(unittest.TestCase):
    def test_agreed_targets_and_order(self):
        self.assertEqual(
            TARGETS,
            (
                ("minecraft:the_nether", 1000),
                ("minecraft:overworld", 8000),
                ("minecraft:the_end", 8000),
            ),
        )


class ProgressResponseTests(unittest.TestCase):
    def test_no_running_tasks(self):
        self.assertEqual(parse_running_worlds("[Chunky] No tasks running.\n\x1b[0m"), set())

    def test_running_world(self):
        self.assertEqual(
            parse_running_worlds(
                "[Chunky] Task running for minecraft:the_nether. Processed: 42 chunks (4.00%)"
            ),
            {"minecraft:the_nether"},
        )

    def test_unrecognized_progress_is_an_error(self):
        with self.assertRaises(ValueError):
            parse_running_worlds("command failed")


class CompletionLogTests(unittest.TestCase):
    def test_only_finish_after_marker_counts(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "latest.log"
            finish = "[Chunky] Task finished for minecraft:the_nether. Processed: 100 chunks (100.00%)\n"
            path.write_text(finish, encoding="utf-8")
            marker = log_marker(path)
            self.assertFalse(finish_logged_since(path, marker, "minecraft:the_nether"))
            with path.open("a", encoding="utf-8") as log_file:
                log_file.write(finish)
            self.assertTrue(finish_logged_since(path, marker, "minecraft:the_nether"))


class ControllerGateTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        self.chunky_dir = root / "chunky"
        self.chunky_dir.mkdir()
        self.server_log = root / "latest.log"
        self.server_log.write_text("", encoding="utf-8")
        self.state = CampaignState(root / "state.json")
        self.state.load()

    def make_controller(self, responses, clock=lambda: 0):
        rcon = FakeRcon(responses)
        controller = Controller(
            rcon,
            self.state,
            self.chunky_dir,
            self.server_log,
            resume_delay=30,
            clock=clock,
        )
        return controller, rcon

    def test_player_present_never_starts_generation(self):
        controller, rcon = self.make_controller(
            {"list": "There are 1 of a max of 20 players online: alice"}
        )
        self.assertTrue(controller.step())
        self.assertEqual(rcon.commands, ["list"])
        self.assertIsNone(self.state.active)

    def test_empty_server_starts_first_target(self):
        controller, rcon = self.make_controller(
            {
                "list": "There are 0 of a max of 20 players online:",
                "chunky progress": "[Chunky] No tasks running.",
                "execute unless entity @a run chunky start minecraft:the_nether circle 0 0 1000": (
                    "[Chunky] Task started in minecraft:the_nether for the circle region"
                ),
            }
        )
        self.assertTrue(controller.step())
        self.assertEqual(
            rcon.commands,
            [
                "list",
                "chunky progress",
                "execute unless entity @a run chunky start minecraft:the_nether circle 0 0 1000",
            ],
        )
        self.assertEqual(self.state.active["world"], "minecraft:the_nether")

    def test_player_arrival_pauses_active_task(self):
        self.state.active = {"world": "minecraft:the_nether", "phase": "started"}
        controller, rcon = self.make_controller(
            {
                "list": "There are 1 of a max of 20 players online: alice",
                "chunky pause minecraft:the_nether": (
                    "[Chunky] Task paused for minecraft:the_nether."
                ),
            }
        )
        self.assertTrue(controller.step())
        self.assertEqual(rcon.commands, ["list", "chunky pause minecraft:the_nether"])

    def test_player_joining_between_checks_blocks_start(self):
        controller, rcon = self.make_controller(
            {
                "list": "There are 0 of a max of 20 players online:",
                "chunky progress": "[Chunky] No tasks running.",
                "execute unless entity @a run chunky start minecraft:the_nether circle 0 0 1000": "",
            }
        )
        self.assertTrue(controller.step())
        self.assertEqual(rcon.commands[-1], "execute unless entity @a run chunky start minecraft:the_nether circle 0 0 1000")
        self.assertIsNone(self.state.active)

    def test_reconnect_delay_holds_paused_task(self):
        self.state.active = {"world": "minecraft:the_nether", "phase": "started"}
        now = [0]
        controller, rcon = self.make_controller(
            {
                "list": "There are 1 of a max of 20 players online: alice",
                "chunky pause minecraft:the_nether": (
                    "[Chunky] Task paused for minecraft:the_nether."
                ),
            },
            clock=lambda: now[0],
        )
        self.assertTrue(controller.step())
        rcon.responses["list"] = "There are 0 of a max of 20 players online:"
        now[0] = 29
        self.assertTrue(controller.step())
        self.assertEqual(rcon.commands[-1], "list")

    def test_bad_player_count_does_not_start_generation(self):
        controller, rcon = self.make_controller({"list": "unexpected response"})
        with self.assertRaises(ValueError):
            controller.step()
        self.assertEqual(rcon.commands, ["list"])

    def test_paused_task_resumes_only_for_its_world(self):
        self.state.active = {"world": "minecraft:the_nether", "phase": "started"}
        task_path = self.chunky_dir / "tasks" / "minecraft" / "the_nether.properties"
        task_path.parent.mkdir(parents=True)
        task_path.write_text(
            "world=minecraft:the_nether\n"
            "cancelled=false\n"
            "center-x=0.0\n"
            "center-z=0.0\n"
            "radius=1000.0\n"
            "shape=circle\n",
            encoding="utf-8",
        )
        controller, rcon = self.make_controller(
            {
                "list": "There are 0 of a max of 20 players online:",
                "chunky progress": "[Chunky] No tasks running.",
                "execute unless entity @a run chunky continue minecraft:the_nether": (
                    "[Chunky] Task continuing for minecraft:the_nether."
                ),
            }
        )
        self.assertTrue(controller.step())
        self.assertEqual(
            rcon.commands[-1],
            "execute unless entity @a run chunky continue minecraft:the_nether",
        )

    def test_player_joining_between_checks_blocks_continue(self):
        self.state.active = {
            "world": "minecraft:the_nether",
            "phase": "started",
            "log_marker": {"inode": 1, "offset": 2},
        }
        task_path = self.chunky_dir / "tasks" / "minecraft" / "the_nether.properties"
        task_path.parent.mkdir(parents=True)
        task_path.write_text(
            "world=minecraft:the_nether\n"
            "cancelled=false\n"
            "center-x=0.0\n"
            "center-z=0.0\n"
            "radius=1000.0\n"
            "shape=circle\n",
            encoding="utf-8",
        )
        controller, rcon = self.make_controller(
            {
                "list": "There are 0 of a max of 20 players online:",
                "chunky progress": "[Chunky] No tasks running.",
                "execute unless entity @a run chunky continue minecraft:the_nether": "",
            },
            clock=lambda: 100,
        )
        self.assertTrue(controller.step())
        self.assertEqual(rcon.commands[-1], "execute unless entity @a run chunky continue minecraft:the_nether")
        self.assertEqual(self.state.active["log_marker"], {"inode": 1, "offset": 2})
        self.assertEqual(controller.last_player_seen, 100)
        self.assertTrue(controller.step())
        self.assertEqual(rcon.commands[-1], "list")

    def test_unexpected_start_response_is_an_error(self):
        controller, _ = self.make_controller(
            {
                "list": "There are 0 of a max of 20 players online:",
                "chunky progress": "[Chunky] No tasks running.",
                "execute unless entity @a run chunky start minecraft:the_nether circle 0 0 1000": (
                    "[Chunky] Start rejected"
                ),
            }
        )
        with self.assertRaises(ControllerError):
            controller.step()

    def test_unrelated_running_task_blocks_campaign(self):
        controller, rcon = self.make_controller(
            {
                "list": "There are 0 of a max of 20 players online:",
                "chunky progress": (
                    "[Chunky] Task running for minecraft:overworld. Processed: 42 chunks (1.00%)"
                ),
            }
        )
        with self.assertRaises(ControllerError):
            controller.step()
        self.assertEqual(rcon.commands, ["list", "chunky progress"])


if __name__ == "__main__":
    unittest.main()
