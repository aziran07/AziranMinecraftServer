"""Check that the pinned BlueMap build has a reachable server map route."""

import json
import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BlueMapDeploymentTests(unittest.TestCase):
    def test_pinned_server_mod_matches_26_3_neoforge(self):
        lock = json.loads((ROOT / "mods-26.3.lock.json").read_text())
        matches = [mod for mod in lock["mods"] if mod.get("project_id") == "swbUV1cr"]
        self.assertEqual(len(matches), 1)
        mod = matches[0]
        self.assertEqual(mod["version_id"], "1EXOwqA2")
        self.assertEqual(mod["filename"], "bluemap-5.27-neoforge.jar")
        self.assertEqual(mod["sha512"], "10d4739243996b40d20330a78582ef405715351fb50b543194595da8cea8f9bbf9ee6d7aba8586653f42a7f6113c9f0e04b5bf61e42ac5a47c3152ea0c4b7c82")
        self.assertIn("26.3", mod["game_versions"])
        self.assertIn("neoforge", mod["loaders"])
        self.assertEqual(lock["mod_count"], len(lock["mods"]))

    def test_https_proxy_reaches_bluemap_without_publishing_map_or_admin_ports(self):
        env = os.environ.copy()
        env.update({
            "RCON_PASSWORD": "test-only",
            "ADMIN_NAME": "test-only",
            "ADMIN_PASSWORD": "test-only",
            "WSS_URL": "wss://example.invalid",
            "WS_URL": "ws://example.invalid",
        })
        env.pop("CLOUDFLARE_TUNNEL_TOKEN", None)
        result = subprocess.run(
            ["docker", "compose", "config", "--format", "json"],
            cwd=ROOT, env=env, capture_output=True, text=True, check=True,
        )
        services = json.loads(result.stdout)["services"]
        self.assertEqual(services["minecraft"]["environment"]["STOP_DURATION"], "600")
        self.assertEqual(services["minecraft"]["stop_grace_period"], "11m0s")
        ports = services["minecraft"]["ports"]
        self.assertFalse(any(port["target"] in (8100, 4326, 4327) for port in ports))
        self.assertIn("8100/tcp", services["minecraft"]["expose"])
        self.assertNotIn("cloudflared", services)
        proxy = services["webmap-nginx"]
        self.assertEqual(
            [(port["published"], port["target"], port["protocol"]) for port in proxy["ports"]],
            [("443", 443, "tcp")],
        )
        self.assertTrue(set(proxy["networks"]) & set(services["minecraft"]["networks"]))
        self.assertEqual(proxy["depends_on"]["minecraft"]["condition"], "service_started")
        volumes = {volume["target"]: volume for volume in proxy["volumes"]}
        for target in (
            "/etc/nginx/conf.d/default.conf",
            "/etc/nginx/cert.pem",
            "/etc/nginx/key.pem",
        ):
            self.assertTrue(volumes[target]["read_only"])

    def test_webmap_proxy_mounts_tls_certificate_and_key(self):
        http = (ROOT / "nginx/webmap.conf").read_text()
        stream = (ROOT / "nginx/templates/minecraft.conf.template").read_text()
        self.assertIn("listen 443 ssl;", http)
        self.assertIn("server_name mcmap.aziran.uk;", http)
        self.assertIn("ssl_certificate /etc/nginx/cert.pem;", http)
        self.assertIn("ssl_certificate_key /etc/nginx/key.pem;", http)
        self.assertIn("proxy_pass http://minecraft:8100;", http)
        self.assertNotIn("localhost:8123", http)
        self.assertNotIn("minecraft:8123", stream)


if __name__ == "__main__":
    unittest.main()
