# JupyterHub

> [!WARNING]
> This repository is work in progress, its content could change at any time.

JupyterHub based on docker compose for short workshops:

- **proxy**: `configurable-http-proxy`, the public entrypoint on port 8000
- **hub**: JupyterHub with `SharedPasswordAuthenticator` and `DockerSpawner`
- **user servers**: one JupyterLab container per user (`jupyter-<username>`), from the image built from `singleuser/Dockerfile`, with `/home/jovyan` bind-mounted from `$USER_STORAGE_DIR/<username>` on the host (default `/data/storage/users`)
- **shared folder**: `$SHARED_DIR` on the host (default `/data/storage/shared`) is mounted read-only at `~/shared` for all users; put workshop material there

Participants log in with any username (lowercase letters, digits, `_ . -`) and the shared workshop password. Idle servers are stopped after `CULL_TIMEOUT` seconds; their files stay on the host.

## JupyterLab image

The user image (`singleuser/`) is built by GitHub Actions (`.github/workflows/build-singleuser.yml`) and pushed to `ghcr.io/<github-owner>/workshop-singleuser` whenever `singleuser/` changes on `main`. Pull requests only test the build.

To prepare an image for a workshop:

1. Add packages (conda-forge) to `singleuser/environment.yml` and push to `main`.
2. Optionally create a git tag, e.g. `git tag v2026.10 && git push --tags`, to get a readable image tag. Every build is also tagged `sha-<commit>`.
3. The first time, make the package public on GitHub (Packages → package settings → visibility), or run `docker login ghcr.io` on the server.

Use a fixed tag in `.env`, not `latest`: the hub only pulls images it does not have yet, so a newer `latest` would not be picked up.

Keep the `hub-X.Y.Z` tag in `singleuser/Dockerfile` equal to the JupyterHub version in `hub/Dockerfile`.

## Setup

```bash
cp .env.example .env
# edit .env: set CONFIGPROXY_AUTH_TOKEN (openssl rand -hex 32),
# JUPYTERHUB_SHARED_PASSWORD, DOCKER_NOTEBOOK_IMAGE,
# and optionally the admin settings
mkdir -p /data/storage/users /data/storage/shared  # or set USER_STORAGE_DIR / SHARED_DIR in .env
```

## Deploy

```bash
docker pull ghcr.io/cloud-nes/jupyter-singleuser:<tag>
docker compose build
docker compose up -d
```

Open <http://localhost:8000>. To switch to a new image, pull it, update `DOCKER_NOTEBOOK_IMAGE` in `.env` and run `docker compose up -d`; user servers get the new image on their next start.

To test changes to `singleuser/` locally without CI:

```bash
docker compose --profile build build singleuser
```

ands set `DOCKER_NOTEBOOK_IMAGE=jupyter-singleuser:dev` in `.env`.

## Operate

```bash
docker compose logs -f hub                    # hub logs
docker ps --filter name=jupyter-              # running user servers
docker compose down                           # stop hub and proxy
docker rm -f $(docker ps -aq --filter name=jupyter-)   # stop all user servers
```

Web apps that users start inside their server (e.g. on port 8001) are reachable via `jupyter-server-proxy` at `http://<hub-host>:8000/user/<username>/proxy/8001/`, only for that user (and admins).

Admins (`JUPYTERHUB_ADMIN_USERS`, logging in with `JUPYTERHUB_ADMIN_PASSWORD`) can manage servers at `/hub/admin`.

## After the workshop

User files are in `$USER_STORAGE_DIR/<username>`. To reset everything:

```bash
docker compose down -v            # also removes the hub database volume
sudo rm -rf /data/storage/users/*  # USER_STORAGE_DIR; deletes all user data!
```
