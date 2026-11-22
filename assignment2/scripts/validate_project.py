"""Fast dependency-light structural checks; runs before expensive integration tests."""
from pathlib import Path
import ast
import yaml

ROOT = Path(__file__).resolve().parents[1]
for path in [ROOT / "ACEest_Fitness.py", *sorted((ROOT / "aceest_fitness").rglob("*.py")), *sorted((ROOT / "tests").rglob("*.py"))]:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

for strategy in ("rolling", "blue-green", "canary", "shadow", "ab"):
    path = ROOT / "k8s" / "strategies" / strategy / "manifest.yaml"
    objects = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    deployments = [o for o in objects if o.get("kind") == "Deployment"]
    services = [o for o in objects if o.get("kind") == "Service"]
    ingresses = [o for o in objects if o.get("kind") == "Ingress"]
    assert deployments and services and ingresses, f"Incomplete strategy: {strategy}"
    for deployment in deployments:
        spec = deployment["spec"]
        assert spec["strategy"]["rollingUpdate"]["maxUnavailable"] == 0
        assert spec["selector"]["matchLabels"] == spec["template"]["metadata"]["labels"]
        c = spec["template"]["spec"]["containers"][0]
        assert c.get("readinessProbe") and c.get("livenessProbe")
        assert c["image"] in ("__IMAGE__", "__CANDIDATE_IMAGE__")
    for service in services:
        selector = service["spec"]["selector"]
        assert any(all(d["spec"]["template"]["metadata"]["labels"].get(k) == v for k, v in selector.items()) for d in deployments)
    names = {service["metadata"]["name"] for service in services}
    for ingress in ingresses:
        for rule in ingress["spec"]["rules"]:
            for route in rule["http"]["paths"]:
                assert route["backend"]["service"]["name"] in names
    print(f"OK: {strategy}: {len(deployments)} deployments, {len(services)} services, {len(ingresses)} ingresses")

for common in (ROOT / "k8s" / "common").glob("*.yaml"):
    assert all(o.get("apiVersion") and o.get("kind") for o in yaml.safe_load_all(common.read_text(encoding="utf-8")))

print("OK: Python source parsed, all five Kubernetes deployment configurations validated")
