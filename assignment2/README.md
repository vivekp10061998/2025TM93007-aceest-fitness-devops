# ACEest Fitness & Gym | BITS Pilani DevOps Assignment 2

This is a **working project implementation** for the assigned Flask/Pytest/Jenkins/SonarQube/Docker/Kubernetes pipeline, adapted from the **10 supplied desktop Tkinter versions**. Those originals are preserved without changes in `legacy_versions/`; a Tkinter GUI cannot be used as an HTTP-based Kubernetes deployment, which is why this repo introduces a Flask web adaptation.

**Status: source and configuration ready for verification.** It does **not** claim an existing GitHub URL, a successful Jenkins run, a passing SonarQube gate, published Docker images or a live Kubernetes endpoint. Those require running commands using your accounts and laptop/cluster.

## Project map

| Path | Purpose |
|---|---|
| `ACEest_Fitness.py` + `aceest_fitness/` | Flask app, HTML dashboard and REST API |
| `legacy_versions/` | All 10 original assignment versions, unchanged |
| `tests/` | 22 Pytest cases (members, progress, health, version, shadow) |
| `Dockerfile`, `docker-compose.yml` | Multi-stage test/runtime images; app plus PostgreSQL |
| `Jenkinsfile` | Poll Git, test in container, SonarQube, gate, versioned build, push, optional deploy/rollback |
| `sonar-project.properties` | SonarQube scan and coverage settings |
| `k8s/common/` | Persistent PostgreSQL and configuration |
| `k8s/strategies/` | All five isolated deployment strategy demonstrations |
| `scripts/` | Deployment, cut-over, smoke test and rollback |
| `docs/` | Report, practical setup and evidence checklist |

## Prerequisites on Windows

Install **Git, Python 3.11+, Docker Desktop** (Linux containers, WSL2 enabled), **Minikube, kubectl**. For full CI/CD you also need Jenkins (with Docker CLI available to its agent), SonarQube and scanner plugin, GitHub, Docker Hub, and the NGINX Ingress add-on in Minikube. Prefer 4 CPUs/8 GiB for local Kubernetes/Jenkins/SonarQube together; extra RAM helps.

### Quick local Flask test (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest -q tests --cov=aceest_fitness --cov-report=xml:coverage.xml
python ACEest_Fitness.py
```

Then open **http://127.0.0.1:8000**. Local mode defaults to SQLite. SQLAlchemy auto-creates the development tables. To use PostgreSQL, use Docker Compose:

```powershell
Copy-Item .env.example .env
# IMPORTANT: change the DB_PASSWORD value inside .env first.
docker compose up --build -d
curl.exe http://localhost:8000/health/ready
```

### Docker image and test stages

```powershell
docker build --target test -t aceest-test .
docker run --rm aceest-test pytest -q tests
docker build --target runtime --build-arg APP_VERSION=3.2.4-web -t YOURUSER/aceest-fitness:3.2.4-web .
docker run --rm -p 8000:8000 YOURUSER/aceest-fitness:3.2.4-web
# To publish after logging in:
docker login
docker push YOURUSER/aceest-fitness:3.2.4-web
```

`YOURUSER` is **a placeholder**. Build/push new release tags from real Flask commits, not by pretending legacy Tkinter versions are web releases. Test image includes Pytest; runtime image does not.

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Demo dashboard |
| GET | `/health/live`, `/health/ready` | Liveness and DB-backed readiness |
| GET | `/api/version`, `/api/programs`, `/api/stats` | Version, program catalog, summary |
| GET/POST | `/api/members` | List/register members |
| GET/PATCH/DELETE | `/api/members/{id}` | Find/update/delete member |
| GET/POST | `/api/members/{id}/progress` | Progress history and entry |

Example: `POST /api/members` JSON: `{"name":"Aarav Patil","email":"aarav@example.com","age":28,"weight_kg":78.5,"program":"fat-loss"}`. The calorie figure is a demo heuristic from historic program-style factors, **not medical/nutrition advice**.

## Git and GitHub versioning

This ZIP includes a **local Git repository with two meaningful commits and a `v3.2.4-web` tag**. Your GitHub account/repository are **not** connected. After extracting the ZIP, verify that the hidden `.git` folder is present and run:

```bash
git status
git log --oneline
git tag
# Create a new EMPTY public GitHub repository first.
git remote add origin https://github.com/YOUR_GITHUB_USER/aceest-fitness-devops.git
git push -u origin main --tags
# For subsequent work:
git switch -c feature/progress-report
# make changes, commit, push branch and open a pull request
```

If your extraction tool discards the hidden `.git` directory, initialize Git with `git init -b main`, stage and commit the project, then set the remote. Change the placeholder GitHub username. Your own Git user.name/user.email should be configured before future commits.

To demonstrate meaningful incremental releases, use multiple real code commits/tags and Jenkins/Docker Hub builds rather than copying version numbers onto identical images.

## Jenkins + SonarQube setup (required for final proof)

1. Create a **Jenkins multibranch pipeline** connected to the GitHub repository, with a Jenkins agent that has access to Docker, shell, `git`, `sonar-scanner` and `kubectl`. Jenkins + Docker socket access is privileged; restrict it to a trusted local/isolated runner.
2. Install/configure Jenkins: Pipeline, Git, GitHub Branch Source, Credentials Binding, JUnit, SonarQube Scanner for Jenkins. Add a SonarQube server named **`SonarQube`**, register the SonarQube token, and ensure `sonar-scanner` executable is on the agent PATH.
3. Configure SonarQube webhook **`http(s)://YOUR-JENKINS-URL/sonarqube-webhook/`** (trailing slash required) so Jenkins `waitForQualityGate` finishes. Configure and pass a server-side Quality Gate.
4. Add Jenkins credentials: `dockerhub-credentials` (username + access token), `kubeconfig` (file), `aceest-db-password` (secret text). Do **not** put secrets in Git or screenshots.
5. Set pipeline parameter **`DOCKERHUB_REPOSITORY`** to `yourdockerhubuser/aceest-fitness`; run initially with `DEPLOY_TO_MINIKUBE=false`, then enable it when the Jenkins agent can reach Minikube. The pipeline polls SCM every ~5 minutes (and can also be triggered by GitHub webhooks).
6. Set branch `main`; recent successful runs and Sonar screenshots are **evidence to collect**, not pre-generated evidence.

## Kubernetes and all five deployment strategies

First: `minikube start --cpus=4 --memory=6144` then `minikube addons enable ingress`. Run the following **Bash scripts in Git Bash/WSL** (or Jenkins Linux agent); they are not PowerShell scripts. `kubectl` context must point to Minikube. On Windows PowerShell, configure the environment variable as `$env:DB_PASSWORD = 'a-strong-local-password'`, then execute bash through Git Bash/WSL.

```bash
export DB_PASSWORD='CHANGE_TO_A_STRONG_LOCAL_PASSWORD'
# All use public, existing images in Docker Hub:
./scripts/apply-strategy.sh rolling YOURUSER/aceest-fitness:3.2.4-web
./scripts/apply-strategy.sh blue-green YOURUSER/aceest-fitness:3.2.4-web YOURUSER/aceest-fitness:NEW_RELEASE
./scripts/apply-strategy.sh canary YOURUSER/aceest-fitness:3.2.4-web YOURUSER/aceest-fitness:NEW_RELEASE
./scripts/apply-strategy.sh shadow YOURUSER/aceest-fitness:3.2.4-web YOURUSER/aceest-fitness:NEW_RELEASE
./scripts/apply-strategy.sh ab YOURUSER/aceest-fitness:3.2.4-web YOURUSER/aceest-fitness:NEW_RELEASE
```

Each strategy has its **own namespace**, DB and ingress hostname so configurations don't conflict (though deploying all five simultaneously uses significant local resources). For single-strategy local validation, start with Rolling. `NEW_RELEASE` is a **placeholder** and must be replaced with a real uploaded app version. For private Docker Hub images, add an imagePullSecret and `imagePullSecrets` to deployments; example assumes public images.

| Strategy | Namespace | Ingress hostname | Mechanism | Rollback |
|---|---|---|---|---|
| Rolling | `aceest-rolling` | `rolling.aceest.test` | `maxUnavailable: 0`, 2 replicas, readiness probe | `./scripts/rollback.sh rolling` |
| Blue-Green | `aceest-blue-green` | `bluegreen.aceest.test` | Service selector blue ⇄ green after candidate health | `./scripts/rollback.sh blue-green blue` |
| Canary | `aceest-canary` | `canary.aceest.test` | NGINX canary ingress with 10% weight | `./scripts/rollback.sh canary` (weight→0) |
| Shadow | `aceest-shadow` | `shadow.aceest.test` | NGINX request mirroring; candidate writes blocked | `./scripts/rollback.sh shadow` (turn off mirror) |
| A/B | `aceest-ab` | `ab.aceest.test` | `X-ACEest-Variant: B` header chooses B | `./scripts/rollback.sh ab` (remove B ingress) |

**Blue-Green cut-over:** `./scripts/switch-blue-green.sh green` after both deployments are healthy, then `./scripts/switch-blue-green.sh blue` to revert. Candidate no longer receives normal traffic after rollback. Shadow mirrors request paths and intentionally suppresses body forwarding; write methods on the shadow candidate return 204, so mirrored requests do not write to the database.

### Access and prove the running endpoint

Local NGINX ingress requires routing the hostnames above to Minikube's ingress IP and potentially running `minikube tunnel` in another terminal (depending on your driver/platform). On Windows Docker Desktop/Minikube driver, `minikube ip` may not be directly reachable from Windows; use Minikube tunnel or a local port-forward to the ingress controller. Test a host-specific ingress with:

```bash
kubectl -n ingress-nginx port-forward service/ingress-nginx-controller 8080:80
curl -H 'Host: rolling.aceest.test' http://127.0.0.1:8080/health/ready
curl -H 'Host: ab.aceest.test' -H 'X-ACEest-Variant: B' -i http://127.0.0.1:8080/api/version
```

That `127.0.0.1:8080` URL is **local only** and not a public cluster endpoint. If the university needs a publicly accessible URL, run your Kubernetes deployment on a cloud cluster with a load balancer or accessible ingress and use the actual public URL. A Minikube localhost or `.test` URL is not generally accessible to your evaluator.

## Screenshot evidence and final submission

Use `docs/VERIFICATION_CHECKLIST.md` and `docs/SETUP_WINDOWS.md`. Capture actual GitHub, Jenkins (green recent build), SonarQube dashboard/gate, Docker Hub tags, `kubectl get all -n ...`, each strategy's ingress/version headers, rollback evidence, and the **actual accessible endpoint URL**. A prewritten report is supplied; update its runtime outcomes based on actual evidence. A source project ZIP by itself does **not** satisfy the live proof obligations.

## Production limitations / reliability notes

This is a classroom demonstration, not a hardened customer-data system. It has no authentication/authorization or database schema migrations; do not store real personal data or expose write APIs to the public internet. Database persistence is backed by a PostgreSQL PVC within each strategy's namespace; production would use managed PostgreSQL, TLS, secrets management, migrations, backup/restore, and deployment monitoring. `maxUnavailable: 0` and readiness gates support zero-downtime rolling changes but do **not guarantee** zero downtime on a resource-constrained single-node cluster or during incompatible DB migrations. Shadow mirrors network traffic but does not provide analytical response diffing; A/B routes by header, not a randomized experiment. These are explicit scope limitations.
