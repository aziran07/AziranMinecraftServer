"""Exercise the scheduled world backup without touching the live server."""

import os
from pathlib import Path
import subprocess
import tarfile
from tempfile import TemporaryDirectory
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
BACKUP_SCRIPT = ROOT / "mc_backup.sh"


class WorldBackupTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.world = self.root / "world"
        self.world.mkdir()
        (self.world / "level.dat").write_bytes(b"test world")
        self.backups = self.root / "backups"
        self.backups.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.command_log = self.root / "rcon-commands.log"
        docker = self.bin / "docker"
        docker.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"$*\" >> \"$MC_BACKUP_TEST_COMMAND_LOG\"\n"
            "case \"$*\" in\n"
            "  *save-off)\n"
            "    if [ \"${MC_BACKUP_TEST_FAIL_SAVE_OFF:-0}\" = 1 ]; then\n"
            "      echo 'save-off reply lost' >&2; exit 1\n"
            "    fi\n"
            "    echo 'Saving is now disabled';;\n"
            "  *save-all\\ flush)\n"
            "    if [ \"${MC_BACKUP_TEST_FAIL_FLUSH:-0}\" = 1 ]; then\n"
            "      echo 'save failed' >&2; exit 1\n"
            "    fi\n"
            "    echo 'Saved the game';;\n"
            "  *save-on)\n"
            "    if [ \"${MC_BACKUP_TEST_FAIL_SAVE_ON:-0}\" = 1 ]; then\n"
            "      echo 'save-on failed' >&2; exit 1\n"
            "    fi\n"
            "    echo 'Saving is now enabled';;\n"
            "  *) echo 'unexpected RCON command' >&2; exit 2;;\n"
            "esac\n",
            encoding="utf-8",
        )
        docker.chmod(0o755)

    def run_backup(self, **overrides):
        script = BACKUP_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("MC_BACKUP_WORLD_DIR", script, "backup script must honor the test world path")
        self.assertIn("MC_BACKUP_DIR", script, "backup script must honor the test output path")
        env = os.environ.copy()
        env.update({
            "PATH": f"{self.bin}:{env['PATH']}",
            "MC_BACKUP_WORLD_DIR": str(self.world),
            "MC_BACKUP_DIR": str(self.backups),
            "MC_BACKUP_TEST_COMMAND_LOG": str(self.command_log),
        })
        env.update(overrides)
        return subprocess.run(
            ["bash", str(BACKUP_SCRIPT)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

    def commands(self):
        return self.command_log.read_text(encoding="utf-8").splitlines()

    def test_success_creates_restorable_archive_and_prunes_only_old_regular_backups(self):
        old_archive = self.backups / "26.3-world-old.tar"
        old_archive.write_bytes(b"old")
        unrelated_file = self.backups / "operator-note.txt"
        unrelated_file.write_text("keep", encoding="utf-8")
        old_time = time.time() - 720 * 60
        os.utime(old_archive, (old_time, old_time))
        os.utime(unrelated_file, (old_time, old_time))

        result = self.run_backup()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.commands(),
            [
                "exec aziran-minecraft-26-3 rcon-cli save-off",
                "exec aziran-minecraft-26-3 rcon-cli save-all flush",
                "exec aziran-minecraft-26-3 rcon-cli save-on",
            ],
        )
        archives = list(self.backups.glob("26.3-world-*.tar"))
        self.assertEqual(len(archives), 1)
        with tarfile.open(archives[0]) as archive:
            self.assertTrue(any(name.endswith("world/level.dat") for name in archive.getnames()))
        self.assertFalse(old_archive.exists())
        self.assertTrue(unrelated_file.exists())
        self.assertFalse(list(self.backups.glob("*.partial")))

    def test_tar_failure_restores_saving_and_keeps_older_backup(self):
        old_archive = self.backups / "26.3-world-old.tar"
        old_archive.write_bytes(b"old")
        old_time = time.time() - 720 * 60
        os.utime(old_archive, (old_time, old_time))
        tar = self.bin / "tar"
        tar.write_text("#!/bin/sh\necho 'tar failed' >&2\nexit 42\n", encoding="utf-8")
        tar.chmod(0o755)

        result = self.run_backup()

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.commands()[-1], "exec aziran-minecraft-26-3 rcon-cli save-on")
        self.assertTrue(old_archive.exists())
        self.assertEqual(list(self.backups.glob("26.3-world-*.tar")), [old_archive])
        self.assertFalse(list(self.backups.glob("*.partial")))

    def test_flush_failure_restores_saving_without_creating_backup(self):
        result = self.run_backup(MC_BACKUP_TEST_FAIL_FLUSH="1")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.commands()[-1], "exec aziran-minecraft-26-3 rcon-cli save-on")
        self.assertFalse(list(self.backups.iterdir()))

    def test_save_off_error_still_attempts_to_restore_saving(self):
        result = self.run_backup(MC_BACKUP_TEST_FAIL_SAVE_OFF="1")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(
            self.commands(),
            [
                "exec aziran-minecraft-26-3 rcon-cli save-off",
                "exec aziran-minecraft-26-3 rcon-cli save-on",
            ],
        )
        self.assertFalse(list(self.backups.iterdir()))

    def test_save_on_failure_keeps_old_backup_and_reports_failure(self):
        old_archive = self.backups / "26.3-world-old.tar"
        old_archive.write_bytes(b"old")
        old_time = time.time() - 720 * 60
        os.utime(old_archive, (old_time, old_time))

        result = self.run_backup(MC_BACKUP_TEST_FAIL_SAVE_ON="1")

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(old_archive.exists())
        self.assertEqual(list(self.backups.glob("26.3-world-*.tar")), [old_archive])
        self.assertIn("save-on", self.commands()[-1])

    def test_missing_world_fails_before_changing_server_saving(self):
        result = self.run_backup(MC_BACKUP_WORLD_DIR=str(self.root / "missing"))

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.command_log.exists())
        self.assertFalse(list(self.backups.iterdir()))


if __name__ == "__main__":
    unittest.main()
