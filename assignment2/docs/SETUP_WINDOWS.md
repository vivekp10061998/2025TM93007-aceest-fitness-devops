# Windows quick-start (simple Hinglish)

**CI = code ko automatically test/build karna. CD = tested code ko deployment tak le jaana.** Browser mein app dikhna alag baat hai; university ko Jenkins → Pytest → SonarQube → Docker Hub → Kubernetes ke *actual proof* chahiye.

## Step 1: Local app

Open project in VS Code, then PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest -q tests
python ACEest_Fitness.py
```

Open http://localhost:8000; form fill karo. Running command stop with Ctrl+C.

## Step 2: Docker

Install Docker Desktop and open it before running commands. Run:

```powershell
Copy-Item .env.example .env
notepad .env
# DB_PASSWORD ko strong password se replace karo.
docker compose up --build -d
curl.exe http://localhost:8000/health/ready
```

To stop: `docker compose down` (data volume is retained).

## Step 3: GitHub and Docker Hub

Create an empty GitHub repo named `aceest-fitness-devops` and Docker Hub repo named `aceest-fitness`. Follow commands in `README.md` to push. Never paste account passwords/tokens into files or chat. Docker `docker login` uses a personal access token.

## Step 4: Jenkins and SonarQube

Run these on a trusted machine with adequate RAM (or install on a cloud lab). Jenkins is the conductor: it reads `Jenkinsfile` and executes all stages. SonarQube is the code-quality checker. The `README.md` lists plugins and required credential *IDs*. Customize the Docker Hub repo parameter and link GitHub. A successful Jenkins build page and quality gate need to be **captured from actual execution**.

## Step 5: Minikube and deployment strategies

Install `kubectl` and `minikube`. Start Minikube and NGINX Ingress as shown in README. Download/push the actual application image first. Use Git Bash or WSL to run `scripts/apply-strategy.sh`. Try Rolling first, then Blue-Green, Canary, Shadow, A/B.

For local proof without editing Windows hosts file, one terminal:

```powershell
kubectl -n ingress-nginx port-forward service/ingress-nginx-controller 8080:80
```

Another terminal:

```powershell
curl.exe -H "Host: rolling.aceest.test" http://localhost:8080/api/version
curl.exe -H "Host: ab.aceest.test" -H "X-ACEest-Variant: B" http://localhost:8080/api/version
```

Save actual screenshots for each strategy's version headers and after rollback. The report must not claim unexecuted stages as tested.

## What I need from you to get the actual account-specific submission done

- **GitHub username and repo URL** (once created), and confirmation the repo is public.
- **Docker Hub username** and image repository URL (never share password/token).
- Whether your Windows PC has Docker Desktop/Minikube/Jenkins/SonarQube installed and enough RAM.
- If university requires an externally reachable endpoint, access to a public Kubernetes cluster or a university-provided lab endpoint.
- Last: screenshots/logs after actual Jenkins/SonarQube/Kubernetes runs to finalize an evidence-backed report.
