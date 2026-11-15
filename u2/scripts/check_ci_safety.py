"""Fail-closed guard for current U2 roots. Does not execute Terraform or cloud code."""
from pathlib import Path
import argparse
import hashlib

import hcl2

try:
    from hcl2.utils import SerializationOptions
except ImportError:
    SerializationOptions = None

BASE = Path(__file__).resolve().parents[1]
ROOTS = {"u2": None, "u2/aws": "aws", "u2/azure": "azurerm"}
VERSIONS = {"aws": "6.42.0", "azurerm": "4.65.0"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def scalar(value):
    return value[0] if isinstance(value, list) and len(value) == 1 else value


def load(path):
    def clean(value):
        if isinstance(value, dict):
            return {key: clean(child) for key, child in value.items() if key not in ("__is_block__", "__comments__")}
        if isinstance(value, list):
            return [clean(child) for child in value]
        return value
    with path.open(encoding="utf-8") as stream:
        if SerializationOptions is not None:
            return clean(hcl2.load(stream, serialization_options=SerializationOptions(strip_string_quotes=True)))
        return clean(hcl2.load(stream))


def local_source(source, parent, base=BASE):
    require(isinstance(source, str) and source.startswith(("./", "../")), "External/dynamic module source forbidden")
    target = (parent / source).resolve()
    require(target.is_relative_to(base.resolve()), "Module escapes U2")
    return target


def check_tests(doc, provider):
    require(not any(k in doc for k in ("provider", "override_module", "test")), "Real provider, module override or test settings forbidden")
    mocks = doc.get("mock_provider", [])
    if provider is None:
        require(not mocks, "Pure root must not acquire a provider")
    else:
        require(len(mocks) == 1 and set(mocks[0]) == {provider}, "Exactly one unaliased expected mock provider required")
        require("alias" not in mocks[0][provider] and "source" not in mocks[0][provider], "Mock alias/external source forbidden")
    runs = []
    for block in doc.get("run", []):
        for name, body in block.items():
            require(scalar(body.get("command")) in ("plan", "${plan}"), "Tests must be plan-only")
            require(not any(k in body for k in ("providers", "override_module")), "Run provider/module overrides forbidden")
            runs.append((name, body))
    return runs


def walk_config(folder, provider, visited, base=BASE):
    if folder in visited:
        return
    visited.add(folder)
    paths = list(folder.glob("*.tf"))
    require(paths and not list(folder.glob("*.tf.json")), "Missing HCL or unsupported JSON configuration")
    for path in paths:
        doc = load(path)
        require(not any(k in doc for k in ("data", "import", "removed")), f"Data/import/removed forbidden: {path}")
        def inspect(value):
            if isinstance(value, dict):
                require("provisioner" not in value, f"Provisioner forbidden: {path}")
                for child in value.values():
                    inspect(child)
            elif isinstance(value, list):
                for child in value:
                    inspect(child)
        inspect(doc)
        for block in doc.get("resource", []):
            require(provider is not None and all(kind.startswith(provider + "_") for kind in block), f"Unexpected resource: {path}")
        for block in doc.get("provider", []):
            require(provider is not None and set(block) == {provider}, f"Unexpected provider: {path}")
            require("alias" not in block[provider], f"Unmocked provider alias: {path}")
        for terraform in doc.get("terraform", []):
            require("cloud" not in terraform, "Remote execution forbidden")
            for requirements in terraform.get("required_providers", []):
                require(provider is not None and set(requirements) == {provider}, "Unexpected provider dependency")
                specification = scalar(requirements[provider])
                require(scalar(specification.get("source")) == "hashicorp/" + provider, "Unexpected provider source")
                require(scalar(specification.get("version")).replace(" ", "") == "=" + VERSIONS[provider], "Provider version must match fixed U2 selection")
                require("configuration_aliases" not in specification, "Provider aliases forbidden")
        for block in doc.get("module", []):
            for body in block.values():
                require("providers" not in body, "Module provider remapping forbidden")
                walk_config(local_source(scalar(body.get("source")), folder, base), provider, visited, base)


def audit(root_name, base=BASE):
    require(root_name in ROOTS, "Only u2, u2/aws and u2/azure may be tested")
    folder = base if root_name == "u2" else base / root_name.split("/")[1]
    folder = folder.resolve()
    provider = ROOTS[root_name]
    visited = set()
    walk_config(folder, provider, visited, base)
    require(not list(folder.glob("*.tftest.hcl")) and not list(folder.glob("*.tftest.json")), "Root-level test entry points forbidden")
    require(not list((folder / "tests").glob("*.tftest.json")), "JSON test entry points forbidden")
    files = sorted((folder / "tests").glob("*.tftest.hcl"))
    require(len(files) == (1 if provider is None else 2), "Unexpected test file count")
    count = 0
    for path in files:
        for name, body in check_tests(load(path), provider):
            for module in body.get("module", []):
                walk_config(local_source(scalar(module["source"]), folder, base), provider, visited, base)
            count += 1
    require(count == 6, "Expected exactly six audited runs")
    template = base / "templates/user_data_u2.sh.tpl"
    require(hashlib.sha256(template.read_bytes()).hexdigest() == "4445eadace792b80ac3e07886d99b80bfd1f250b892731dfc9abda77b9c9e2e3", "Official template changed")
    if provider:
        lock = load(folder / ".terraform.lock.hcl")
        expected = "registry.terraform.io/hashicorp/" + provider
        require(len(lock.get("provider", [])) == 1 and expected in lock["provider"][0], "Missing/unexpected provider lock")
        require(scalar(lock["provider"][0][expected].get("version")) == VERSIONS[provider], "Unexpected locked version")
    print(f"PASS {root_name}: local modules, six plan-only runs, expected mocks, template and lock")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", choices=ROOTS)
    audit(parser.parse_args().root)
