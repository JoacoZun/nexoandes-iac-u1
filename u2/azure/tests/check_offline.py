"""Guard previo a terraform test: solo provider Azure mock, plan local y módulos locales."""
from pathlib import Path
import hashlib
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("u2_ci_guard", ROOT.parent / "scripts/check_ci_safety.py")
_guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_guard)
scalar = lambda value: value[0] if isinstance(value, list) and len(value) == 1 else value
runs = []
for path in (ROOT / "tests").glob("*.tftest.hcl"):
    doc = _guard.load(path)
    assert not any(k in doc for k in ("provider", "override_module")), path
    assert len(doc.get("mock_provider", [])) == 1, path
    assert "azurerm" in doc["mock_provider"][0], path
    for block in doc.get("run", []):
        for name, body in block.items():
            assert scalar(body.get("command")) in ("plan", "${plan}"), name
            assert "providers" not in body, name
            for module in body.get("module", []):
                assert scalar(module["source"]).startswith("./"), name
            runs.append(name)
assert len(runs) == 6, runs
for path in ROOT.rglob("*.tf"):
    if ".terraform" in path.parts:
        continue
    doc = _guard.load(path)
    assert "data" not in doc, path
    assert "provisioner" not in path.read_text(encoding="utf-8"), path
    for block in doc.get("resource", []):
        assert all(kind.startswith("azurerm_") for kind in block), path
template = ROOT.parent / "templates/user_data_u2.sh.tpl"
assert hashlib.sha256(template.read_bytes()).hexdigest() == "4445eadace792b80ac3e07886d99b80bfd1f250b892731dfc9abda77b9c9e2e3"
print("SAFETY PASS: plantilla intacta; 6 runs mock Azure, plan-only, sin data/provisioners")
print("\n".join(runs))
