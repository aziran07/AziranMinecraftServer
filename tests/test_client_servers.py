"""Check the default multiplayer entry in each generated client archive."""

import io
from pathlib import Path
import struct
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.1.9"


def read_string(stream):
    length = struct.unpack(">H", stream.read(2))[0]
    return stream.read(length).decode("utf-8")


def read_server_list(data):
    """Read the small, standard NBT shape used by Minecraft servers.dat."""
    stream = io.BytesIO(data)
    assert stream.read(1) == b"\x0a"  # root compound
    assert read_string(stream) == ""
    assert stream.read(1) == b"\x09"  # list tag
    assert read_string(stream) == "servers"
    assert stream.read(1) == b"\x0a"  # list of compounds
    count = struct.unpack(">i", stream.read(4))[0]
    servers = []
    for _ in range(count):
        entry = {}
        while (tag := stream.read(1)) != b"\x00":
            assert tag == b"\x08"  # string tag
            key = read_string(stream)
            entry[key] = read_string(stream)
        servers.append(entry)
    assert stream.read() == b"\x00"  # root end, no extra data
    return servers


class ClientServerTests(unittest.TestCase):
    def test_each_distribution_includes_aziran_multiplayer_entry(self):
        paths = {
            f"aziran-26.3-client-{VERSION}.mrpack": "client-overrides/servers.dat",
            f"aziran-26.3-client-{VERSION}-manual.zip": "servers.dat",
            f"aziran-26.3-client-{VERSION}-multimc.zip": ".minecraft/servers.dat",
        }
        for archive_name, server_path in paths.items():
            with self.subTest(archive=archive_name):
                with zipfile.ZipFile(ROOT / "dist" / archive_name) as archive:
                    self.assertEqual(archive.namelist().count(server_path), 1)
                    servers = read_server_list(archive.read(server_path))
                    self.assertEqual(len(servers), 1)
                    self.assertEqual(servers[0]["ip"], "mc.aziran.uk")
                    self.assertTrue(servers[0]["name"])


if __name__ == "__main__":
    unittest.main()
