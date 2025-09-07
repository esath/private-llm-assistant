# GitHub Actions CI and Docker Hub Secrets

## What the workflow does
- Builds and pushes two Docker images (backend and frontend) to Docker Hub on every push to the `main` branch.

## How it’s triggered
- on: push to branches: `main`
- Add `workflow_dispatch` if you want manual runs.

## Where the workflow must live
- Workflows run only from `.github/workflows/*.yml` or `*.yaml`.
- Ensure the file path is `.github/workflows/ci-cd.yaml`.

## Job and steps (summary)
- Runs on `ubuntu-latest`.
- Steps:
  - `actions/checkout@v3`: Fetches the repository.
  - `docker/setup-buildx-action@v2`: Enables BuildKit/Buildx.
  - `docker/login-action@v2`: Logs in to Docker Hub using secrets:
    - `DOCKERHUB_USERNAME`
    - `DOCKERHUB_TOKEN`
  - `docker/build-push-action@v4` (backend):
    - `context: ./backend`, `file: ./backend/Dockerfile`, `push: true`
    - `tags: <username>/ollama-rag-backend:latest`
  - `docker/build-push-action@v4` (frontend):
    - `context: ./frontend`, `file: ./frontend/Dockerfile`, `push: true`
    - `tags: <username>/ollama-rag-frontend:latest`

## Requirements in the repo
- `backend/Dockerfile` and `frontend/Dockerfile` must exist and build.
- Repo secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` configured.

## Outputs
- Two images pushed:
  - `<username>/ollama-rag-backend:latest`
  - `<username>/ollama-rag-frontend:latest`

## Notes and tips
- Tagging: Add immutable tags (e.g., `:sha-${{ github.sha }}`) alongside `:latest` for traceability.
- Caching/multi-arch: Use `cache-to/cache-from` and `platforms: linux/amd64,linux/arm64` if needed.
- Argo CD: Prefer immutable image tags in k8s manifests; avoid relying solely on `:latest`.

---

## Storing Docker Hub credentials (GitHub Actions secrets)

1. Create a Docker Hub access token:
   - Open: `"$BROWSER" https://hub.docker.com/settings/security`
   - Click “New Access Token” and copy it.

2. Add repository secrets in GitHub:
   - Repo → Settings → Secrets and variables → Actions.
   - New repository secret:
     - Name: `DOCKERHUB_USERNAME`
     - Value: your Docker Hub username
   - New repository secret:
     - Name: `DOCKERHUB_TOKEN`
     - Value: the access token from Docker Hub

3. Notes
   - Names are case-sensitive and must match the workflow.
   - For multiple repos, use Organization secrets: Org → Settings → Secrets and variables → Actions.
   - For environment-specific secrets, create an Environment and add secrets there; target that environment in the workflow job.

For more on GitHub Actions secrets, see: `"$BROWSER" https://docs.github.com/actions/security-guides/encrypted-secrets`
