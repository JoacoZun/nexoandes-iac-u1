"""Regression tests for CI guard: unsafe changes must fail before Terraform runs."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import re
import unittest
import yaml

SPEC = importlib.util.spec_from_file_location("u2_ci_guard", Path(__file__).resolve().parents[1] / "scripts/check_ci_safety.py")
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)


class CiGuardTests(unittest.TestCase):
    def test_workflow_has_no_deployment_or_credentials(self):
        path = GUARD.BASE.parent / ".github/workflows/u2-ci.yml"
        doc = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        self.assertEqual(doc["permissions"], {"contents": "read"})
        self.assertEqual(set(doc["on"]), {"push", "pull_request"})
        for trigger in doc["on"].values():
            self.assertEqual(set(trigger["paths"]), {"u2/**", ".github/workflows/u2-ci.yml"})
        job = doc["jobs"]["offline"]
        self.assertEqual(set(job["strategy"]["matrix"]["root"]), set(GUARD.ROOTS))
        commands = []
        for step in job["steps"]:
            if "uses" in step:
                self.assertRegex(step["uses"], r"@[a-f0-9]{40}$")
            commands.append(step.get("run", ""))
        text = "\n".join(commands)
        self.assertIsNone(re.search(r"\b(apply|destroy|plan)\b", text))
        self.assertIn("-backend=false", text)
        self.assertIn("-lockfile=readonly", text)
        self.assertIn("bash u2/scripts/run_offline_linux.sh", text)
        self.assertIn("test_observation*.py", text)
        wrapper = (GUARD.BASE / "scripts/run_offline_linux.sh").read_text()
        self.assertIn("sudo -n unshare --net", wrapper)
        self.assertIn("ip link set lo up", wrapper)
        self.assertIn("--no-new-privs", wrapper)
        self.assertIn("--bounding-set=-all", wrapper)
        self.assertLess(wrapper.index('"$python_bin" -B u2/scripts/ci_network_probe.py'), wrapper.index('exec "$@"'))
        self.assertNotIn("|| true", wrapper)
        self.assertNotIn("secrets.", path.read_text())
        self.assertNotIn("--allow-network", text)
        self.assertNotIn("--allow-network", wrapper)
        self.assertNotIn("environment", job)

    def test_current_roots_pass(self):
        for root in GUARD.ROOTS:
            GUARD.audit(root)

    def test_missing_mock_and_apply_are_rejected(self):
        for doc in [{"run": [{"unsafe": {"command": "plan"}}]},
                    {"mock_provider": [{"aws": {}}], "run": [{"unsafe": {"command": "apply"}}]}]:
            with self.assertRaises(ValueError):
                GUARD.check_tests(doc, "aws")

    def test_real_provider_and_mapping_are_rejected(self):
        for extra in ["provider", "override_module"]:
            with self.assertRaises(ValueError):
                GUARD.check_tests({extra: [], "mock_provider": [{"aws": {}}]}, "aws")
        with self.assertRaises(ValueError):
            GUARD.check_tests({"mock_provider": [{"aws": {}}], "run": [{"unsafe": {"command": "plan", "providers": {}}}]}, "aws")

    def test_external_and_escaping_modules_are_rejected(self):
        for source in ["git::https://example.invalid/module", "../../outside"]:
            with self.assertRaises(ValueError):
                GUARD.local_source(source, GUARD.BASE)

    def test_data_provisioner_and_alias_are_rejected(self):
        cases = ['data "aws_ami" "unsafe" {}',
                 'resource "aws_instance" "unsafe" {\n provisioner "local-exec" {\n command = "echo forbidden"\n }\n}\n',
                 'provider "aws" { alias = "unsafe" }']
        for code in cases:
            with TemporaryDirectory() as name:
                root = Path(name).resolve()
                (root / "main.tf").write_text(code, encoding="utf-8")
                with self.assertRaises(ValueError):
                    GUARD.walk_config(root, "aws", set(), root)


if __name__ == "__main__":
    unittest.main()
