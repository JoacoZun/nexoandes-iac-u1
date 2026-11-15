"""Pruebas offline: sin sockets, bootstrap, cloud, Terraform ni escrituras de state."""
import ast
import base64
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates/user_data_u2.sh.tpl"
EXPECTED_SHA = "4445eadace792b80ac3e07886d99b80bfd1f250b892731dfc9abda77b9c9e2e3"
TEXT = TEMPLATE.read_text(encoding="utf-8")
EXPRESSION = "${base64encode(jsonencode({provider = provider, x = x, student = student, course = course, build_ref = build_ref, portal_version = portal_version}))}"
SOURCE = TEXT.split("<<'PYTHON'\n", 1)[1].split("\nPYTHON\n", 1)[0]
APP = {"__name__": "offline_portal_test"}
exec(compile(SOURCE, "official_portal_base.py", "exec"), APP)


def config(provider="aws", version="v1"):
    return dict(provider=provider, x=8, student="a008", course="c99",
                build_ref="offline-test", portal_version=version)


class LocalBaseTests(unittest.TestCase):
    def test_official_bytes_and_lf(self):
        raw = TEMPLATE.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SHA)
        self.assertNotIn(b"\r", raw)

    def test_all_supported_configs_and_size(self):
        # Emula SOLO la sustitución JSON/base64; no sustituye terraform test.
        self.assertEqual(TEXT.count("${"), 1)
        self.assertIn(EXPRESSION, TEXT)
        for provider, version in [("aws", "v1"), ("aws", "v2"), ("azure", "v1")]:
            c = config(provider, version)
            self.assertEqual(APP["validate_config"](c), c)
            encoded = base64.b64encode(json.dumps(c, separators=(",", ":")).encode()).decode()
            rendered = TEXT.replace(EXPRESSION, encoded)
            self.assertNotIn("${", rendered)
            self.assertLessEqual(len(rendered.encode()), 16384)
        largest = dict(config("aws", "v2"), x=254, student="a254", build_ref="f" * 80)
        encoded = base64.b64encode(json.dumps(largest, separators=(",", ":")).encode()).decode()
        self.assertLessEqual(len(TEXT.replace(EXPRESSION, encoded).encode()), 16384)

    def test_invalid_identity_and_azure_v2_rejected(self):
        for changes in [dict(x=255), dict(x=True), dict(student="a007"),
                        dict(course="c1"), dict(build_ref="$(id)"),
                        dict(provider="azure", portal_version="v2")]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                APP["validate_config"](dict(config(), **changes))

    def test_distinct_real_release_code(self):
        installer = TEXT.split("<<'INSTALL_RELEASE'\n", 1)[1].split("\nINSTALL_RELEASE\n", 1)[0]
        tree = ast.parse(installer)
        node = next(n for n in tree.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "releases" for t in n.targets))
        releases = ast.literal_eval(node.value)
        self.assertNotEqual(releases["v1"], releases["v2"])
        self.assertIn("basic", releases["v1"])
        self.assertIn("extended", releases["v2"])
        for source in releases.values():
            compile(source, "portal_release.py", "exec")

    def test_aws_imdsv2_no_real_network(self):
        calls = []
        def fetch(path, headers=None, method="GET"):
            calls.append((path, headers, method))
            if method == "PUT":
                return "synthetic-test-token"
            self.assertEqual(headers["X-aws-ec2-metadata-token"], "synthetic-test-token")
            return {"instance-id": "i-synthetic", "availability-zone": "test-zone",
                    "local-ipv4": "10.8.10.4"}[path.rsplit("/", 1)[-1]]
        result = APP["cloud_metadata"]("aws", fetch)
        self.assertEqual(result["private_ip"], "10.8.10.4")
        self.assertEqual(calls[0][2], "PUT")

    def test_azure_imds_no_real_network(self):
        def fetch(path, headers=None, method="GET"):
            self.assertEqual(headers, {"Metadata": "true"})
            return json.dumps({"compute": {"vmId": "synthetic-vm", "name": "test",
                                           "location": "test-location"},
                               "network": {"interface": [{"ipv4": {"ipAddress": [
                                   {"privateIpAddress": "172.20.8.4"}]}}]}})
        self.assertEqual(APP["cloud_metadata"]("azure", fetch)["resource_id"], "synthetic-vm")

    def test_failed_refresh_preserves_cache_but_fails_function(self):
        state = APP["MetadataState"]()
        self.assertFalse(state.snapshot()["metadata_ok"])
        def good(path, headers=None, method="GET"):
            return "10.8.10.4" if path.endswith("local-ipv4") else "synthetic"
        state.refresh("aws", good)
        self.assertTrue(state.snapshot()["metadata_ok"])
        def broken(*args):
            raise TimeoutError("synthetic failure")
        state.refresh("aws", broken)
        info = APP["make_info"](config(), "v1", "basic", "synthetic-hash", state)
        self.assertTrue(info["metadata_cached"])
        self.assertTrue(info["metadata_stale"])
        self.assertFalse(APP["functional_check"](info, "basic")["passed"])

    def test_no_cloud_resources_backends_or_providers_in_base(self):
        paths = list(ROOT.glob("*.tf")) + list((ROOT / "modules").rglob("*.tf"))
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r'^\s*(resource|data|provider|backend)\s+"', text, re.M), str(path))
        self.assertNotIn("fase1/", (ROOT / "outputs.tf").read_text())

    def test_aws_tests_always_mock_plan_only(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("u2_ci_guard", ROOT / "scripts/check_ci_safety.py")
        guard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(guard)
        scalar = lambda v: v[0] if isinstance(v, list) and len(v) == 1 else v
        runs = 0
        for path in (ROOT / "aws/tests").glob("*.tftest.hcl"):
            doc = guard.load(path)
            self.assertNotIn("provider", doc)
            self.assertEqual(len(doc.get("mock_provider", [])), 1)
            self.assertIn("aws", doc["mock_provider"][0])
            for run in doc.get("run", []):
                for body in run.values():
                    self.assertIn(scalar(body["command"]), ("plan", "${plan}"))
                    self.assertNotIn("providers", body)
                    runs += 1
        self.assertEqual(runs, 6)


if __name__ == "__main__":
    unittest.main()
