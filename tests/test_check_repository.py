"""Regresión offline con HCL real y archivos temporales; no invoca Terraform/AWS."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import unittest

# El Python embebido de Checkov no añade el cwd a sys.path; cargar el archivo
# exacto evita depender de esa diferencia de entorno o de paquetes llamados scripts.
_spec = importlib.util.spec_from_file_location(
    "repository_checker", Path(__file__).resolve().parents[1] / "scripts/check_repository.py"
)
_checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_checker)
check_network_policy = _checker.check_network_policy
collect_resources = _checker.collect_resources


HTTP = '''
resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = "sg-fixture-only"
  ip_protocol = "tcp"
  from_port = 80
  to_port = 80
  cidr_ipv4 = "0.0.0.0/0"
}
'''
LEGACY_HTTP = '''
resource "aws_security_group_rule" "http" {
  security_group_id = "sg-fixture-only"
  type = "ingress"
  protocol = "tcp"
  from_port = 80
  to_port = 80
  cidr_blocks = ["0.0.0.0/0"]
}
'''
EGRESS = '''
resource "aws_vpc_security_group_egress_rule" "bootstrap" {
  for_each = toset(["80", "443"])
  security_group_id = "sg-fixture-only"
  ip_protocol = "tcp"
  from_port = tonumber(each.value)
  to_port = tonumber(each.value)
  cidr_ipv4 = "0.0.0.0/0"
}
'''
LEGACY_EGRESS = '''
resource "aws_security_group_rule" "outbound" {
  security_group_id = "sg-fixture-only"
  type = "egress"
  protocol = "tcp"
  from_port = 443
  to_port = 443
  cidr_blocks = ["0.0.0.0/0"]
}
'''


class RepositoryPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "modules/security/main.tf"
        self.source.parent.mkdir(parents=True)

    def resources(self, hcl):
        self.source.write_text(hcl, encoding="utf-8")
        return collect_resources(self.root)

    def accepted(self, hcl):
        check_network_policy(self.resources(hcl))

    def rejected(self, hcl, message):
        with self.assertRaisesRegex(SystemExit, message):
            check_network_policy(self.resources(hcl))

    def test_parser_recognizes_quoted_resource_labels(self):
        resources = self.resources(HTTP)
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0][:2], ("aws_vpc_security_group_ingress_rule", "http"))
        check_network_policy(resources)

    def test_single_public_http_is_accepted(self):
        self.accepted(HTTP)

    def test_modern_egress_is_not_ingress(self):
        self.accepted(HTTP + EGRESS)

    def test_legacy_egress_is_not_ingress(self):
        self.accepted(HTTP + LEGACY_EGRESS)

    def test_legacy_public_http_is_fully_validated_and_accepted(self):
        self.accepted(LEGACY_HTTP + LEGACY_EGRESS)

    def test_egress_cannot_satisfy_required_ingress(self):
        self.rejected(EGRESS + LEGACY_EGRESS, "Exactly one ingress")

    def test_ssh_is_rejected_in_both_resource_types(self):
        for http in (HTTP, LEGACY_HTTP):
            with self.subTest(resource=http.splitlines()[1]):
                self.rejected(http.replace("= 80", "= 22"), "incorrect port range")

    def test_second_modern_ingress_is_rejected(self):
        self.rejected(HTTP + HTTP.replace('"http"', '"extra"'), "Exactly one ingress")

    def test_second_legacy_ingress_cannot_bypass_policy(self):
        self.rejected(HTTP + LEGACY_HTTP, "Exactly one ingress")

    def test_incorrect_protocol_is_rejected(self):
        for http in (HTTP, LEGACY_HTTP):
            for protocol in ('"udp"', '"-1"', 'var.protocol'):
                with self.subTest(resource=http.splitlines()[1], protocol=protocol):
                    self.rejected(http.replace('"tcp"', protocol), "incorrect protocol")

    def test_incorrect_port_or_range_is_rejected(self):
        for http in (HTTP, LEGACY_HTTP):
            for replacement in ("to_port = 81", "to_port = 443", "to_port = var.port"):
                with self.subTest(resource=http.splitlines()[1], replacement=replacement):
                    self.rejected(http.replace("to_port = 80", replacement), "incorrect port range")

    def test_incorrect_source_is_rejected(self):
        for http in (HTTP, LEGACY_HTTP):
            for source in ("10.0.0.0/8", "::/0", "0.0.0.0/1"):
                with self.subTest(resource=http.splitlines()[1], source=source):
                    self.rejected(http.replace("0.0.0.0/0", source), "incorrect source")

    def test_legacy_multiple_sources_are_rejected(self):
        self.rejected(LEGACY_HTTP.replace('["0.0.0.0/0"]',
                                         '["0.0.0.0/0", "10.0.0.0/8"]'), "incorrect source")

    def test_additional_source_selector_is_rejected(self):
        self.rejected(HTTP.replace('  ip_protocol', '  referenced_security_group_id = "sg-other"\n  ip_protocol'),
                      "incorrect source")
        self.rejected(LEGACY_HTTP.replace('  protocol', '  self = true\n  protocol'), "incorrect source")

    def test_legacy_unknown_direction_fails_closed(self):
        for direction in ('"unknown"', "var.direction", "null"):
            with self.subTest(direction=direction):
                rule = LEGACY_EGRESS.replace('"egress"', direction)
                self.rejected(HTTP + rule, "Unknown rule direction")

    def test_inline_ingress_is_rejected(self):
        inline = '''resource "aws_security_group" "extra" {
          ingress { from_port = 22 }
        }'''
        self.rejected(HTTP + inline, "Inline ingress forbidden")

    def test_dynamic_inline_ingress_is_rejected(self):
        inline = '''resource "aws_security_group" "extra" {
          dynamic "ingress" {
            for_each = [22]
            content { from_port = ingress.value }
          }
        }'''
        self.rejected(HTTP + inline, "Dynamic inline ingress forbidden")

    def test_count_or_for_each_cannot_hide_multiple_or_zero_ingress(self):
        for meta in ("count = 0", "count = 2", "count = var.n", "for_each = { a = 80, b = 80 }"):
            for http in (HTTP, LEGACY_HTTP):
                with self.subTest(resource=http.splitlines()[1], meta=meta):
                    self.rejected(http.replace('  security_group_id', f'  {meta}\n  security_group_id'),
                                  "exactly one static instance")

    def test_explicit_single_instance_is_accepted(self):
        for http in (HTTP, LEGACY_HTTP):
            with self.subTest(resource=http.splitlines()[1]):
                self.accepted(http.replace('  security_group_id', '  count = 1\n  security_group_id'))

    def test_empty_ingress_is_rejected(self):
        self.rejected('', "Exactly one ingress")


if __name__ == "__main__":
    unittest.main()
