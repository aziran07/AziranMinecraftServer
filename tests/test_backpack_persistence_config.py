"""Guard the deployed backpack mode against the Curios 17 lost-write defect.

This checks deployment configuration, not in-game persistence. The runtime
acceptance procedure is documented in docs/BACKPACK_PERSISTENCE.md.
"""

from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BackpackPersistenceConfigTests(unittest.TestCase):
    def test_server_uses_native_backpack_attachment(self):
        path = ROOT / "server-data-26.3-neoforge/config/travelersbackpack-server.toml"
        with path.open("rb") as stream:
            config = tomllib.load(stream)
        self.assertIs(
            config["server"]["backpackSettings"]["backSlotIntegration"],
            False,
            "Curios 17 returns detached stacks: Traveler's Backpack 11.4.0 "
            "must use its native attachment to persist worn contents.",
        )


if __name__ == "__main__":
    unittest.main()
