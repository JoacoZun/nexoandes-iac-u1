"""Checks de estructura/política sin AWS; no reemplaza validate ni Checkov."""
from pathlib import Path
import re

import hcl2
import yaml

try:
    from hcl2.utils import SerializationOptions
except ImportError:
    # bc-python-hcl2, instalado por Checkov, ofrece la API anterior.
    SerializationOptions = None

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def load_hcl(stream):
    if SerializationOptions is not None:
        # python-hcl2 8 conserva comillas en labels Y valores por defecto.
        return hcl2.load(
            stream, serialization_options=SerializationOptions(strip_string_quotes=True)
        )
    return hcl2.load(stream)


def attribute(body, name):
    """Literal escalar: el fork de Checkov lo envuelve en una lista."""
    value = body.get(name)
    return value[0] if isinstance(value, list) and len(value) == 1 else value


def list_attribute(body, name):
    """Conserva tuplas HCL; en el fork están envueltas en otra lista."""
    value = body.get(name)
    if isinstance(value, list) and len(value) == 1 and isinstance(value[0], list):
        return value[0]
    return value


def collect_resources(root=ROOT):
    resources = []
    for path in sorted(root.glob("modules/**/*.tf")):
        with path.open(encoding="utf-8") as stream:
            doc = load_hcl(stream)
        for block in doc.get("resource", []):
            for kind, named in block.items():
                resources.extend((kind, name, body) for name, body in named.items())
    return resources


def check_network_policy(resources):
    ingress = []
    for kind, name, body in resources:
        if kind == "aws_vpc_security_group_ingress_rule":
            ingress.append((kind, name, body))
        elif kind == "aws_security_group_rule":
            direction = attribute(body, "type")
            require(direction in ("ingress", "egress"),
                    f"Unknown rule direction: {kind}.{name}; use literal ingress/egress")
            if direction == "ingress":
                ingress.append((kind, name, body))
        elif kind == "aws_security_group":
            require(not body.get("ingress"),
                    "Inline ingress forbidden: rules must remain independently auditable")
            for dynamic in body.get("dynamic", []):
                require("ingress" not in dynamic,
                        "Dynamic inline ingress forbidden: use independent rules")
        elif kind == "aws_instance":
            require("key_name" not in body, "SSH key provisioning not permitted")

    addresses = ", ".join(f"{kind}.{name}" for kind, name, _ in ingress) or "none"
    require(len(ingress) == 1,
            "Exactly one ingress resource required; no additional SSH/other ingress "
            f"(found {len(ingress)}: {addresses})")
    kind, name, rule = ingress[0]
    # Un bloque con count/for_each podría crear varias reglas o ninguna.
    count = attribute(rule, "count") if "count" in rule else 1
    require("for_each" not in rule and type(count) is int and count == 1,
            f"Ingress must declare exactly one static instance: {kind}.{name}")
    require(attribute(rule, "from_port") == 80 and attribute(rule, "to_port") == 80,
            "Only public TCP/80 ingress allowed: incorrect port range")
    protocol_key = "ip_protocol" if kind == "aws_vpc_security_group_ingress_rule" else "protocol"
    require(attribute(rule, protocol_key) == "tcp",
            "Only public TCP/80 ingress allowed: incorrect protocol")
    if kind == "aws_vpc_security_group_ingress_rule":
        require(attribute(rule, "cidr_ipv4") == "0.0.0.0/0" and all(
            attribute(rule, field) is None
            for field in ("cidr_ipv6", "prefix_list_id", "referenced_security_group_id")
        ), "Only public TCP/80 ingress allowed: incorrect source")
    else:
        require(list_attribute(rule, "cidr_blocks") == ["0.0.0.0/0"] and all(
            list_attribute(rule, field) in (None, [])
            for field in ("ipv6_cidr_blocks", "prefix_list_ids", "security_groups")
        ) and attribute(rule, "self") in (None, False),
            "Only public TCP/80 ingress allowed: incorrect source")


def check_repository(root=ROOT):
    for folder in (root, *(p for p in (root / "modules").iterdir() if p.is_dir())):
        for name in ("main.tf", "variables.tf", "outputs.tf", "versions.tf"):
            path = folder / name
            require(path.is_file() and path.stat().st_size > 0, f"Missing or empty: {path}")
    check_network_policy(collect_resources(root))

    for path in sorted((root / ".github/workflows").iterdir()):
        if path.name.endswith((".yml", ".yaml", ".yml.disabled")):
            # BaseLoader conserva 'on' sin la coerción booleana de YAML 1.1.
            doc = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
            require(isinstance(doc, dict) and "on" in doc and "jobs" in doc,
                    f"Invalid workflow: {path}")
            for job in doc["jobs"].values():
                for step in job.get("steps", []):
                    if "uses" in step:
                        require(re.search(r"@[a-f0-9]{40}$", step["uses"]),
                                f"Action not pinned: {step['uses']}")
    active = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    require(not re.search(r"terraform\s+(apply|destroy|plan)\b", active),
            "Active CI must remain offline")


if __name__ == "__main__":
    check_repository()
    print("PASS: module structure, single HTTP ingress/no SSH key, YAML structure "
          "and action SHA pins; CI has no AWS operations")
