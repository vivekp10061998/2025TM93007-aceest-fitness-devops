# Submission and evidence checklist

Mark a row completed **only after verifying on your actual environment**. Screenshots should include timestamps/build IDs where possible. Never fabricate SonarQube reports, successful Jenkins runs or endpoint URLs.

| Requirement | Proof to capture | Verified? |
|---|---|---|
| Web app and versions | `ACEest_Fitness.py`, `legacy_versions/`, browser page | ☐ |
| GitHub repo | Public GitHub repo URL, at least 2 commits + release tag | ☐ |
| Pytest | Local/container Pytest pass output and JUnit XML | ☐ |
| Jenkins polling | Jenkinsfile + recent green build with commit hash | ☐ |
| SonarQube | Project summary, quality gate status and coverage | ☐ |
| Docker | Docker image builds and container app responds | ☐ |
| Docker Hub | Public repo URL with version tags and SHA-tagged builds | ☐ |
| Kubernetes rolling | Healthy 2 replicas; `/api/version`; rollout revision | ☐ |
| Blue-Green | blue→green switch; traffic versions; green→blue rollback | ☐ |
| Canary | Primary vs 10%-weighted canary ingress; disable to 0% | ☐ |
| Shadow | Mirror ingress and shadow pod logs; disable mirror | ☐ |
| A/B | Header A vs header B versions; remove B ingress | ☐ |
| Rollback | Real `kubectl rollout undo` or service/ingress reversion | ☐ |
| Endpoint | Actual evaluator-accessible endpoint URL, tested externally | ☐ |
| Report | 2–3 page honest summary with actual evidence/status | ☐ |

Commands to support evidence:

```bash
kubectl get deployments,services,ingresses -n aceest-rolling
kubectl rollout history deployment/aceest-app -n aceest-rolling
kubectl get deployments,services,ingresses -n aceest-blue-green
kubectl -n aceest-canary describe ingress aceest-canary
kubectl -n aceest-shadow logs deployment/aceest-shadow --tail=30
kubectl -n aceest-ab describe ingress aceest-variant-b
```

**Important:** A green test suite locally verifies source logic only. It does not mean Jenkins, SonarQube, Docker push, Kubernetes ingress or actual progressive routing were validated.
