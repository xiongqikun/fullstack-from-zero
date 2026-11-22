# Delivery & Operations for a first full-stack app — research brief (key: `delivery-ops-2026`)

Date of all checks: 2026-11-19. Audience: course builders (not the learner). Language of lessons will be Chinese; this brief is English with Chinese analogies in §19.

Basis tags: **[local]** = I ran it on this Mac today; **[source: URL]** = read in a primary source today; **[memory]** = not verified.
Two strengths of [source]: *raw* = I downloaded the page's own Markdown/text and read or grepped it myself; *sum* = a fetch tool's small model summarised the page for me (numbers deserve one re-check before a lesson quotes them). §21 lists which is which.

## 0. What was verified and how

- **Local, no Docker, no accounts, no ports.** Built a throwaway uv project (`lab/shipit`): FastAPI + SQLAlchemy + Alembic + pydantic-settings; ran ruff, pytest (in-process `TestClient`), Alembic upgrade/check/downgrade/`--sql`, a backup→disaster→restore drill on SQLite, `uv export`, `uv sync --locked` failure, `uv build`, in-process OpenTelemetry spans, `app.frontend()` serving a real Vite build, SSH key generation, permissions/signals/exit codes, DNS-over-HTTPS queries, TLS certificate inspection with `curl -v`.
- **Config files validated without Docker/GitHub**: `Dockerfile` linted with hadolint 2.15.1; `compose.yaml` and `compose.prod.yaml` validated against the Compose Specification JSON schema; 4 workflows + `dependabot.yml` validated against GitHub's schemas, actionlint 1.7.12 and zizmor 1.32.0; `fly.toml` parsed as TOML and keys compared with the Fly reference. Every linter was also run on a deliberately broken file to prove it fails (negative tests).
- **Registry/tag existence** checked anonymously (`git ls-remote`, release redirects, GHCR manifest API, docker-library tag files).
- **NOT done (by rule)**: no `docker build/run`, no deployment, no account, no workflow run on GitHub. The Dockerfile is "linted + tags verified", not "built".
- Sandbox-only detail: `uvx` needed `UV_CACHE_DIR` and `UV_TOOL_DIR` pointed at a temp directory here; in a normal terminal plain `uvx <tool>` is enough. Nothing was installed globally.
- **Reachability**: at test time every candidate host answered over HTTPS (github.com, *.github.io, ghcr.io, hub.docker.com, fly.io, render.com, railway.com, vercel.com, netlify.com, cloudflare.com, neon.com, supabase.com, sentry.io, uptimerobot.com, pypi.org, registry.npmjs.org, fastapicloud.com, hetzner.com, google.com) [local]. That says nothing about the learner's own network; test there. Requests go through a local sandbox proxy, so latency numbers are not meaningful.

## 1. Version snapshot (2026-11-19)

| Thing | On this Mac [local] | Latest upstream today | Evidence |
|---|---|---|---|
| uv | 0.13.5 | 0.13.9 | [source: github.com/astral-sh/uv/releases/latest redirect] |
| ruff | 0.17.2 | 0.17.5 | same method |
| Python | 3.14.9 (default), 3.12.15 | images: `python:3.14-slim-trixie` = 3.14.10; newest stable line is **3.15** (3.15.2) | [source: docker-library/official-images/library/python, raw] |
| Docker Desktop | 4.98.0 (read from Info.plist) | 4.99.0 (2026-11-09): Engine 29.9.3, Compose **v5.7.0** | [source: docs.docker.com/desktop/release-notes, sum] |
| Docker Compose | bundled plugin | **v5.8.0** (2026-11-17); all current releases are v5.x | [source: github.com/docker/compose/releases, sum + redirect] |
| PostgreSQL | not installed (no psql/pg_dump) | **18.7** current; 19 RC2 out; image `postgres:latest` = 18.7 | [source: postgresql.org/support/versioning sum; official-images/library/postgres raw] |
| FastAPI / Starlette / uvicorn | 0.165.0 / 1.10.0 / 0.54.0 (lab) | 0.165.0 | [local] |
| SQLAlchemy / Alembic / psycopg | 2.1.9 / 1.20.1 / 3.3.9 (lab) | Alembic 1.20.1 | [local] |
| pytest / pydantic-settings / sentry-sdk | 9.2.0 / 2.16.3 / 2.75.0 (lab) | — | [local] |
| Node / npm / Vite / React / TypeScript | 26.12.0 / 11.20.0 / 8.3.6 / 19.3.1 / 7.0.2 | — | [local] `npm create vite@latest` |
| OpenSSH | 10.5p1 (default KEX `mlkem768x25519-sha256`) | — | [local] `ssh -V`, `ssh -G` |
| Caddy | not installed | 2.11.9 (image `caddy:2.11-alpine`) | [source: caddyserver/caddy release redirect; official-images/library/caddy raw] |
| GitHub CLI `gh` | not installed | 2.105.0 | release redirect |
| Linters | via `uvx` | actionlint 1.7.12, hadolint 2.15.1, zizmor 1.32.0, check-jsonschema 0.39.0 | [local] |

GitHub Actions — latest releases and whether a floating major tag exists [local `git ls-remote` + release redirects]:
`actions/checkout` v7.0.1 (`v7` ✔) · `actions/setup-python` v7.1.0 (`v7` ✔) · `actions/setup-node` v7.1.0 (`v7` ✔) · `actions/cache` v6.1.0 (`v6` ✔) · `actions/upload-artifact` v7.0.2 · `actions/download-artifact` v8.0.2 · `actions/configure-pages` v6.0.0 (`v6` ✔) · `actions/upload-pages-artifact` v5.0.0 (`v5` ✔) · `actions/deploy-pages` v5.0.1 (`v5` ✔) · `docker/login-action` v4.8.0 (`v4` ✔) · `docker/metadata-action` v6.2.0 (`v6` ✔) · `docker/setup-buildx-action` v4.4.1 (`v4` ✔) · `docker/build-push-action` v7.4.0 (`v7` ✔) · `superfly/flyctl-actions` 1.5 · **`astral-sh/setup-uv` v10.3.3 — NO `v10`/`v9`/`v8` tag exists** (see §2).

## 2. Top findings (decision-relevant)

1. **Default capstone path**: one container (FastAPI serving API + built React app) on **Fly.io** (`fra`) + **Neon** Free Postgres (`aws-eu-central-1`) + GitHub Actions CI/CD + Sentry + an uptime monitor (`fra` / `aws-eu-central-1`, Frankfurt, are example regions only; use the region nearest the learner and the users). Expected cost $0/month, but **Fly needs a credit card**. **Fallback**: same Dockerfile on **Render Free** + Neon (no card, ~1 min cold starts). Optional time-boxed lab: one small VPS with Docker Compose + Caddy. Reasons in §16.
2. **Free tiers keep moving — isolate provider steps.** In 2026 alone: Koyeb announced the end of its free Starter plan for new users (joining Mistral AI, 2026-02-17); Heroku moved to a maintenance-only (sustaining engineering) model (2026-02); Hetzner raised cloud prices twice (April, June 15); Netlify is credit-based (a production deploy costs 15 of 300 free credits); Fly.io has no free tier but formally waives personal bills under $5. Keep lessons provider-neutral (Dockerfile, health endpoint, env config, migrations, CI) and put provider steps in thin, re-verifiable "deploy adapter" lessons.
3. **`astral-sh/setup-uv` stopped publishing floating major tags at v8.0.0 (the release that introduced immutable releases)**: `uses: astral-sh/setup-uv@v10` does not resolve; old tutorials' `@v5/@v6/@v7` still resolve to old code. Its README and the uv docs pin a full commit SHA with a version comment [local `git ls-remote`; source: setup-uv README raw; uv docs raw].
4. **Supply-chain hygiene is now mainstream in docs**: uv docs pin every action by SHA; GitHub now recommends a *workflow dependency lockfile* (`.github/workflows/actions.lock`, generated by `gh actions-lock`) as the strongest available protection, with SHA pinning as the fallback [source: docs.github.com/en/actions/reference/security/secure-use; …/concepts/security/workflow-dependency-lockfiles, raw]. Dependabot supports the `uv` ecosystem and a `cooldown` (default 3 days for version updates) [source: dependabot options reference, raw; schema-validated locally].
5. **Official uv-in-Docker pattern changed**: `ENV UV_NO_DEV=1` + `uv sync --locked` (first layer: `--no-install-project` with bind-mounted `uv.lock`/`pyproject.toml` and a cache mount), base `ghcr.io/astral-sh/uv:python3.x-trixie-slim`, non-root user with fixed IDs, multi-stage into `python:3.x-slim-trixie`. The uv *guide* does not discuss non-root; the official *example repo* does [source: uv docs raw; astral-sh/uv-docker-example raw].
6. **FastAPI 0.165 changes deployment teaching**: `fastapi run` is the production command (host 0.0.0.0, `$PORT` honoured, proxy headers on by default); `[tool.fastapi] entrypoint` in `pyproject.toml`; `app.frontend("/", directory="dist")` serves a built SPA with correct fallback; OpenTelemetry is built in (`FASTAPI_OTEL_AUTO_CONFIGURE=true`); the old `tiangolo/uvicorn-gunicorn-fastapi` image is deprecated; `fastapi deploy` targets FastAPI Cloud (public beta) [local + source: fastapi docs raw].
7. **`postgres:18` moved its data directory**: mount the volume at `/var/lib/postgresql`, not `/var/lib/postgresql/data` (17 and older still need `/data`) [source: docker-library/docs postgres/content.md raw].
8. **SQLAlchemy 2.1 uses psycopg 3 for `postgresql://` URLs by default**; `postgres://` (given by some providers) still fails with `NoSuchModuleError` [local; source: neon.com/docs/guides/sqlalchemy-migrations raw].
9. **GitHub Free limits that shape the capstone**: Pages needs a *public* repo; environment secrets, required reviewers and wait timers work only in *public* repos; standard runners are free only for public repos (private: $12/month of included compute ≈ 2,000 Linux minutes at $0.006) [source: docs.github.com … creating-a-github-pages-site; deployments-and-environments; billing … github-actions, raw].
10. **Cloudflare tells new projects to use Workers, not Pages** (a banner at the top of the Pages docs says to start new projects on Workers) [source: developers.cloudflare.com/pages, sum].
11. **Certificates are getting shorter**: Let's Encrypt default drops from 90 to 64 days on 2027-02-10 and to 45 days in 2028; 6-day and IP-address certificates are GA since 2026-01-15 [source: letsencrypt.org/2026/10/07/64-day-certs; /2026/01/15/6day-and-ip-general-availability, sum]. Teach "certificates are automated, never hand-renewed".
12. **DORA now has five delivery metrics** (not four) [source: dora.dev/guides/dora-metrics, sum] — §15.
13. **Privacy trap found locally**: `uv init --package` copies the machine's git `user.name`/`user.email` into `pyproject.toml` `authors`; the `.gitignore` it writes does not contain `.env` [local].

## 3. What changed compared with older tutorials

| Older tutorials say | Today | Basis |
|---|---|---|
| `uses: astral-sh/setup-uv@v5` | Full version tag or SHA only (`@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3`) | [local] |
| `actions/checkout@v3/v4`, `setup-python@v4/v5` | checkout v7, setup-python v7; GitHub's own docs show `checkout@v6`; Fly's docs still show `@v4` and `setup-flyctl@master` (vendor docs lag) | [source: ghdocs raw; docs.fly.io/launch/continuous-deployment-with-github-actions raw] |
| "Pin actions to SHA" is the top advice | Lockfile first, SHA pinning second, tags only for trusted creators | [source: secure-use raw] |
| `uv sync --frozen --no-dev` in Dockerfiles | `ENV UV_NO_DEV=1`, `uv sync --locked` (`--frozen` only where the project files are not yet copied, e.g. workspaces) | [source: uv docs raw] |
| `FROM python:3.x-slim-bookworm` | `-trixie` (Debian 13) variants in uv docs and official images | [source: uv docs raw] |
| `gunicorn -k uvicorn.workers.UvicornWorker`, tiangolo image | `fastapi run` (`--workers N` if needed); one process per container on orchestrators | [source: fastapi docs deployment/docker.md, server-workers.md raw] |
| `pip install -r requirements.txt` in the image | still shown in FastAPI docs, generated by `uv export --format requirements-txt --no-dev --no-emit-project` | [source: fastapi docs raw; local run] |
| `docker-compose.yml` with `version: "3.8"`, `docker-compose` command | `compose.yaml` (preferred name), no `version` (obsolete, warns), `docker compose` (v5 CLI plugin) | [source: docs.docker.com/reference/compose-file/version-and-name sum; compose-application-model raw] |
| `depends_on: [db]` + wait-for-it scripts | `depends_on: {db: {condition: service_healthy}}`, `service_completed_successfully` for one-off migration services | [source: docker/docs compose/how-tos/startup-order.md raw] |
| Postgres volume at `/var/lib/postgresql/data` | `/var/lib/postgresql` for 18+ | [source raw] |
| SQLAlchemy needs `psycopg2-binary` | psycopg 3 is the default driver in SQLAlchemy 2.1 | [local] |
| OpenTelemetry via `opentelemetry-instrumentation-fastapi` | built into FastAPI; enable with env vars | [source: fastapi docs advanced/opentelemetry.md raw; local spans] |
| Docker Hub: unlimited/"100 per 6h" confusion | 100 pulls/6h per IP unauthenticated, 200/6h Personal, 1 private repo | [source: docs.docker.com/docker-hub/usage sum] |
| GitHub Free = "2,000 minutes" | "$12 of included compute" (same thing at $0.006/min Linux 2-core); new 1-vCPU `ubuntu-slim` runner; `ubuntu-latest` = 24.04, `ubuntu-26.04` available | [source: ghdocs raw] |
| cron in Actions is UTC only | optional `timezone:` (IANA name) on `schedule`; public-repo schedules still auto-disable after 60 days without activity | [source: events-that-trigger-workflows raw] |
| "Fly.io has a free tier" / "Heroku free dynos" / "Koyeb free forever" / "Railway $5 free every month" | none of these is true today (§8) | [source] |
| Netlify Free = 100 GB + 300 build minutes | 300 credits/month; production deploy 15 credits, bandwidth 20 credits/GB; sites pause when credits run out | [source: docs.netlify.com … how-credits-work sum] |
| Cloudflare Pages for new static sites | Workers static assets recommended | [source sum] |
| Four DORA keys, MTTR | five metrics; "failed deployment recovery time", "deployment rework rate" | [source sum] |

## 4. Linux essentials for developers

What a developer (not a sysadmin) needs, in this order — content is long-stable [memory] unless tagged:

1. **Files and permissions**: `ls -l`, owner/group/others × r/w/x, octal (`600` private key, `644` file, `755` script/dir), `chmod`, `chown`. [local] real output: `-rw-r--r-- deploy.sh` → `./deploy.sh` → `permission denied` (exit **126**) → `chmod +x` → runs; unknown command → exit **127**.
2. **Processes and signals**: PID/PPID, foreground/background, `ps`, `top`, `kill -TERM` vs `-KILL`. [local] `sleep 300 &; kill -TERM $!; wait $!` → exit status **143** (128+15). Ties directly to Docker: exec-form `CMD` makes the server PID 1 so it receives SIGTERM on deploy/stop.
3. **Environment variables and PATH**: a child process inherits a copy. [local] `APP_ENV=staging sh -c 'echo $APP_ENV'` prints `staging`; the parent still has it unset.
4. **Networking basics**: IP, port, `127.0.0.1` (only this machine) vs `0.0.0.0` (all interfaces — required inside containers), `curl -I`, listening sockets (`ss -tlnp` on Linux, `lsof -i -P` on macOS).
5. **Packages**: `apt update && apt install` (Debian/Ubuntu). In Dockerfiles always in one `RUN` [source: docker best practices sum].
6. **Services (awareness)**: systemd unit = "start at boot, restart on crash"; `systemctl status|start|enable`, `journalctl -u name -f`. Docker's `restart: unless-stopped` is the container-world analogue.
7. **SSH**: key pair (`ssh-keygen -t ed25519 -C "comment"`), public key on the server, private key never leaves the laptop, `~/.ssh/config`, host-key prompt on first connect, `scp`/`rsync`. [local] OpenSSH 10.5p1 generated `-rw------- key` / `-rw-r--r-- key.pub`; the public key is one line `ssh-ed25519 AAAA… comment`.
8. **Server hygiene (VPS lab only)**: non-root sudo user, key-only login, `ufw allow 22,80,443`, unattended security upgrades, never expose the database port.

**macOS is not Linux** [local]: `systemctl`, `journalctl`, `apt`, `ip`, `ss`, `free`, `useradd`, `ufw` do not exist on this Mac (`launchctl` does); BSD tools differ from GNU (`stat -f` vs `stat -c`, `sed -i ''`). Where to practise: (a) `docker run --rm -it ubuntu:24.04 bash` for files, processes, apt (no systemd inside a normal container); (b) a rented VPS for ssh, systemd, firewall. Do not build a big "Linux administration" module.

## 5. Docker and Docker Compose

### 5.1 Official uv pattern today [source: raw.githubusercontent.com/astral-sh/uv/main/docs/guides/integration/docker.md; github.com/astral-sh/uv-docker-example, raw]

- Get uv by `COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /uvx /bin/` or start `FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim`. Pin a version (or a digest); `:latest` appears in docs examples, but the guide itself calls pinning a specific version best practice.
- `ENV UV_NO_DEV=1` (omit dev group), `UV_COMPILE_BYTECODE=1` (faster start), `UV_LINK_MODE=copy` (cache mount is another filesystem), `UV_PYTHON_DOWNLOADS=0` (use the image's Python in multi-stage builds).
- Two-layer install: `uv sync --locked --no-install-project` with `--mount=type=bind` for `uv.lock` + `pyproject.toml` and `--mount=type=cache,target=/root/.cache/uv`; then `COPY . /app` and `uv sync --locked`.
- Put `/app/.venv/bin` first on `PATH`; `.venv` must be in `.dockerignore` (the uv docs call this best practice: the venv is platform-specific).
- The final stage must use the *same* Python image family as the builder, because the venv records the interpreter's path (the example warns that a different Python image will fail).
- Non-root: `groupadd --system --gid 999 nonroot && useradd --system --gid 999 --uid 999 --create-home nonroot`, `COPY --chown`, `USER nonroot`.
- Local dev: `docker compose watch` with `develop.watch` (`sync` the source, ignore `.venv/`, `rebuild` on `uv.lock`); in the example the dev container runs as `root` with `UV_NO_DEV=0`.
- Images are signed; `gh attestation verify --owner astral-sh oci://ghcr.io/astral-sh/uv:<tag>` (awareness).

### 5.2 Dockerfile used in the lab (hadolint: 0 findings; base tags confirmed to exist; **not built**) — `lab/shipit/Dockerfile`

Adapted from the official `multistage.Dockerfile` in `astral-sh/uv-docker-example` (changes: pinned uv tag, Python 3.14, numeric `USER`, `fastapi run` via the pyproject entrypoint).

```dockerfile
# syntax=docker/dockerfile:1
# check=error=true
FROM ghcr.io/astral-sh/uv:0.13.9-python3.14-trixie-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_DEV=1 UV_PYTHON_DOWNLOADS=0
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked

FROM python:3.14-slim-trixie AS runtime
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot
COPY --from=builder --chown=nonroot:nonroot /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
USER 999:999
WORKDIR /app
EXPOSE 8000
CMD ["fastapi", "run", "--port", "8000"]
```

- [local] `ghcr.io/astral-sh/uv:0.13.9-python3.14-trixie-slim` → HTTP 200 from the GHCR manifest API; `python:3.14-slim-trixie` listed in official-images (3.14.10).
- [local] hadolint first reported `DL3066 Non-numeric user-id may not be resolvable by host system` for `USER nonroot`; `USER 999:999` cleared it. On a bad file it reported DL3007 (`latest`), DL3013/DL3042 (pip), DL3020 (`ADD`), DL3025 (shell-form `CMD`).
- `# check=error=true` turns Docker's built-in build checks into errors; `docker build --check .` lints without building [source: docker/docs manuals/build/checks.md raw].
- `CMD ["fastapi","run"]` relies on `[tool.fastapi] entrypoint = "shipit.main:app"` in `pyproject.toml`; [local] fastapi-cli 0.0.34 resolves it (`source: entrypoint-pyproject`). `fastapi run --help` [local]: host default `0.0.0.0`, port default 8000 with `[env var: PORT]`, `--proxy-headers` default on, `--workers`.
- Size hint [local]: the synced environment is 82 MB for 70 packages; `fastapi[standard]` pulls in the FastAPI Cloud CLI and OpenTelemetry SDK (214-line requirements export). `fastapi[standard-no-fastapi-cloud-cli]` exists.

### 5.3 Compose (schema-validated, not run) — `lab/shipit/compose.yaml`

```yaml
name: shipit
services:
  db:
    image: postgres:18
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-shipit}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD in .env}
      POSTGRES_DB: ${POSTGRES_DB:-shipit}
    volumes: ["pgdata:/var/lib/postgresql"]        # 18+: parent dir, not .../data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 3s
      retries: 10
    ports: ["127.0.0.1:5432:5432"]                 # this Mac only, not the LAN
  migrate:
    build: .
    command: ["alembic", "upgrade", "head"]
    env_file: .env
    depends_on: {db: {condition: service_healthy}}
  api:
    build: .
    env_file: .env
    ports: ["127.0.0.1:8000:8000"]
    depends_on:
      db: {condition: service_healthy}
      migrate: {condition: service_completed_successfully}
    healthcheck:   # slim images have no curl
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"]
    develop:
      watch:
        - {action: sync+restart, path: ./src, target: /app/src}
        - {action: rebuild, path: ./uv.lock}
volumes: {pgdata: {}}
```

[local] `uvx check-jsonschema --builtin-schema vendor.compose-spec compose.yaml deploy/vps/compose.prod.yaml` → `ok -- validation done`; a file with `imagee:`/`port:` typos → `Unevaluated properties are not allowed ('imagee', 'port' were unexpected)`, exit 1. Learners with Docker should use `docker compose config` instead (I could not).

### 5.4 Other Docker facts

- Dockerfile best practices still current: multi-stage, minimal trusted base images, `.dockerignore`, one concern per container, pin versions (digest + Dependabot for strictness), `apt-get update && install` in one `RUN`, exec-form `CMD`/`ENTRYPOINT`, `USER` non-root with explicit IDs, `COPY` over `ADD`, absolute `WORKDIR`, rebuild often with `--pull` [source: docs.docker.com/build/building/best-practices sum].
- Docker Desktop is free for personal use, education, non-commercial open source and small businesses (<250 employees AND <$10M revenue) [source: docs.docker.com/subscription/desktop-license sum]. Docker Desktop's Docker.app ships plugins `docker-init`, `docker-compose`, `docker-buildx`, `docker-scout`, `docker-dhi` [local, directory listing].
- Docker Hardened Images: free "Community" tier under Apache 2.0 (non-root by default, SBOM, provenance); uv publishes `-dhi` variants. Awareness only [source: docs.docker.com/dhi sum; uv docs raw].
- Compose in production on one server is legitimate: a second file (`compose.production.yaml`), `restart: always`, no source bind mounts, `docker compose -f a -f b up -d` [source: docker/docs compose/how-tos/production.md raw].
- If the learner's folders are in an iCloud-synced Desktop or another synced folder: bind mounts, `.venv`, `node_modules` and `compose watch` inside iCloud-synced folders are a known source of trouble [memory] — move the workspace (e.g. `~/code`) before the Docker lessons.

## 6. Container registries

| Registry | Free facts today | Use in course |
|---|---|---|
| GHCR (`ghcr.io`) | Public packages free; container image storage and bandwidth are currently not billed at all (GitHub promises at least a month's notice before changing that); push from Actions with `GITHUB_TOKEN` + `packages: write` [source: docs.github.com … billing github-packages, publish-docker-images, raw] | Default: same account as the code |
| Docker Hub | 1 private repo on Personal; pull limits 100/6h anonymous, 200/6h signed in [source sum] | Source of base images; explain rate-limit errors |
| Fly registry (`registry.fly.io`) | Builders and image storage are free for now; images not deployed for a while may be pruned — not a forever rollback target [source: docs.fly.io/about/pricing, /blueprints/rollback-guide raw] | Implicit with `fly deploy` |

Concepts: `registry/owner/name:tag@sha256:digest`; tags move, digests do not; tag images with the git SHA and the release version; a new GHCR package is private until made public [memory].

## 7. CI/CD with GitHub Actions

### 7.1 Facts [source: docs.github.com, raw unless noted]

- Standard runners free in public repos (4 vCPU/16 GB Linux); private repos 2 vCPU/8 GB and metered. A `-latest` label is the latest image GitHub considers stable, not necessarily the newest OS release.
- Secrets: organization, repository, environment levels; encrypted client-side; log redaction is best-effort, not guaranteed; everyone with write access to a repository can effectively read all of its secrets.
- Environments: named targets with secrets/variables and protection rules (≤6 required reviewers, wait timer ≤30 days, branch/tag restrictions). On Free: environment secrets, required reviewers, wait timers only in public repos.
- OIDC: job gets a short-lived signed token (`permissions: id-token: write`) that a cloud exchanges for temporary credentials, so no long-lived cloud secret is stored in GitHub. Repos created after 2026-07-15 use an immutable `sub` format with owner/repo IDs. The learner meets OIDC for real in the Pages deploy job and in PyPI trusted publishing; Fly/Render use stored tokens/hooks.
- Risky triggers: `pull_request_target` and `workflow_run` with untrusted code. [local] zizmor flagged my first draft (`on: workflow_run`) as `error[dangerous-triggers] … almost always used insecurely`; restructuring to one workflow with `needs:` cleared it.
- Push protection for users is enabled by default and blocks pushing recognised secrets to public repos.
- uv in CI [source: uv docs raw]: `astral-sh/setup-uv` (pin `version:`), `uv sync --locked`, `uv run pytest`; cache via `enable-cache`; `uv cache prune --ci` when managing the cache yourself.

### 7.2 Pipeline validated in the lab — `lab/shipit/.github/workflows/ci.yml` (schema ✔, actionlint ✔, zizmor ✔; never executed on GitHub)

```yaml
name: CI/CD
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    concurrency: {group: "test-${{ github.ref }}", cancel-in-progress: true}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with: {persist-credentials: false}
      - uses: astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3
        with: {version: "0.13.9", enable-cache: true}
      - run: uv sync --locked            # fails if uv.lock is stale
      - run: uv run ruff format --check . && uv run ruff check .
      - run: uv run pytest -q
      - run: uv run alembic upgrade head && uv run alembic check
        env: {SHIPIT_DATABASE_URL: "sqlite:///./ci.db"}
  deploy:
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    concurrency: {group: deploy-production, cancel-in-progress: false}
    environment: {name: production, url: "https://shipit-example.fly.dev"}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with: {persist-credentials: false}
      - uses: superfly/flyctl-actions/setup-flyctl@fc53c09e1bc3be6f54706524e3b82c4f462f77be # 1.5
      - run: flyctl deploy --remote-only --env SHIPIT_GIT_SHA="$GITHUB_SHA"
        env: {FLY_API_TOKEN: "${{ secrets.FLY_API_TOKEN }}"}
      - run: curl --fail --silent --show-error --retry 5 --retry-delay 5 https://shipit-example.fly.dev/healthz
```

Also in the lab, all validated the same way: `pages.yml` (configure-pages → upload-pages-artifact → deploy-pages with `pages: write` + `id-token: write`, environment `github-pages`), `image.yml` (buildx → login to ghcr.io with `GITHUB_TOKEN` → metadata → build-push on `v*.*.*` tags), `integration.yml` (Postgres 18 service container with `pg_isready` health options), `.github/dependabot.yml` (`uv`, `github-actions`, `docker` ecosystems with `cooldown`).

Local lint commands that worked [local]: `uvx check-jsonschema --builtin-schema vendor.github-workflows .github/workflows/*.yml` · `uvx --from actionlint-py actionlint` · `uvx zizmor --offline .github` · `uvx --from hadolint-bin hadolint Dockerfile` · `uvx check-jsonschema --builtin-schema vendor.dependabot .github/dependabot.yml`. actionlint on a broken file caught an unknown runner label, a script-injection risk (`github.event.pull_request.title` in `run:`) and double-quoted strings in an expression.

Beginner policy suggestion: SHA + version comment for every action (copy from the action's README), Dependabot keeps them fresh; explain *why* once (tags can be moved), mention lockfiles as the next step.

## 8. Deployment targets (status today)

| Target | Free / cheap tier today | Limits and traps | Fit |
|---|---|---|---|
| **Fly.io** | No free tier. Trial: $1 credit, 7 days, no card, trial Machines stop after 5 min. With a card: personal-org bills **under $5/month are waived** (a $7 bill is charged in full). shared-cpu-1x 256 MB $2.19/30 days (iad), 512 MB $3.69, 1 GB $6.70 (fra $7.73); stopped Machine rootfs $0.15/GB; volumes $0.15/GB; shared IPv4 + IPv6 free, dedicated IPv4 $2; egress $0.02/GB EU/NA, $0.12/GB Africa/India; builders and registry free; first 10 certificates free | No billing alerts yet (the cost-management doc says so and tells you to budget accordingly); `fly deploy`/`fly launch` default `--ha` = 2 Machines; Managed Postgres starts at $38/month (avoid); prepaid cards not accepted as saved method; regions: ams arn cdg dfw ewr fra gru iad jnb lax lhr nrt ord sin sjc syd yyz | **Default** for the capstone. [source: docs.fly.io/about/pricing, free-trial, free-waiver, billing, cost-management, reference/regions, flyctl/cmd/fly_deploy — raw] |
| **Render** | Free web service 0.1 CPU/512 MB, spins down after 15 min idle (~1 min wake), 750 instance-hours/workspace/month; Hobby workspace includes 5 GB bandwidth + 500 pipeline minutes; static sites free; native Python runtime understands `uv.lock` (default uv 0.13.7) | Free services: no shell/SSH, no disks, no one-off jobs, **no pre-deploy command** (paid only), ephemeral filesystem; Free Postgres: 1 GB, **expires 30 days after creation**, no backups; regions oregon/ohio/virginia/frankfurt/singapore | **Fallback** (+ Neon for the DB). [source: render.com/docs/free, deploys, outbound-bandwidth, build-pipeline, uv-version, postgresql-backups, blueprint-spec — raw] |
| Railway | Trial $5 once (30 days, no card); Free plan $1/month credit, 0.5 GB RAM/1 vCPU, 1 project, 3 services, services sleep, no custom domains; Hobby $5/month incl. $5 usage | Automated verification weighs how old and how active the linked GitHub account is — a brand-new account may get a limited trial (restricted outbound network) | Alternative. [source: docs.railway.com/pricing/plans raw; railway.com/pricing, docs…/free-plan sum] |
| Koyeb | Pricing page shows Pro $29/month + compute and a banner about joining Mistral AI; the 2026-02-17 blog post says the Starter plan will be removed soon and new users must pick Pro, Scale or Enterprise | Docs FAQ still describes a free instance — contradictory | **Do not plan on it.** [source: koyeb.com/pricing, blog 2026-02-17, sum] |
| FastAPI Cloud | Hobby $0: 3 apps, 1 custom domain, Nano instances, scale-to-zero, no card; usage is not invoiced yet | Public beta (2026-06); no managed database; hides Docker | Candidate for the *first* backend deploy (`uv run fastapi deploy`). [source: fastapicloud.com/pricing sum; fastapi docs raw; local: `fastapi deploy` command exists] |
| Vercel | Hobby free: 100 GB transfer, 1M function invocations, 4 CPU-hours, 200 projects, 100 deploys/day; zero-config FastAPI as one function (lifespan, WebSockets, `app.frontend`) | Over a limit → wait up to 30 days; `*.vercel.app` unreliable in mainland China (official guide); not a container/ops lesson | Front-end demos. [source: vercel.com/docs/plans/hobby, /docs/frameworks/backend/fastapi raw; KB guide sum] |
| Netlify | Free 300 credits/month | 15 credits per production deploy → ~20 deploys/month, then projects pause | Not for frequent-deploy learners. [source sum] |
| Cloudflare Workers / Pages | Workers Free 100k requests/day, 10 ms CPU; static-asset requests are free and unlimited; Pages Free 500 builds/month, 20,000 files, 25 MiB/file; D1/KV/R2 free quotas | Python Workers are a different runtime (`pywrangler`), not a normal container; Workers custom domains need the domain on Cloudflare DNS | Static/front-end hosting. [source: developers.cloudflare.com workers/platform/pricing, pages/platform/limits, pages, workers/static-assets, sum] |
| Small VPS + Docker Compose + Caddy | Hetzner shared plans now start around €5.5–6/month after two 2026 increases; cheapest lines sometimes "not available" | You own security and patching; needs a domain for normal HTTPS | **Ops lab** (rent for a week, then delete). [source: hetzner.com/cloud sum + third-party reports — weak] |
| **Neon** (Postgres) | Free: 100 projects, 10 branches/project, **100 CU-hours/project/month**, ≤2 CU, **1 GB/project** (20 GB total), 5 GB egress, scale-to-zero after 5 min (cannot disable), 6 h instant restore, 1 manual snapshot; Postgres 14–18; no card needed (neon.com/pricing, sum) | Azure regions deprecated; branded "Lakebase Postgres" (Databricks) in docs; use direct (non `-pooler`) URL for migrations and `pg_dump` | **Default database.** [source: neon.com/docs/introduction/plans, regions, manage/backups, guides/backup-pg-dump raw; connection-pooling sum] |
| Supabase (Postgres + auth) | Free: 2 active projects, 500 MB DB, 5 GB egress, 50k auth MAU | Pauses after 1 week idle; no backups on Free; direct connection is IPv6-only unless paid add-on → use the session pooler on IPv4 networks | Alternative DB. [source: supabase.com/pricing, docs…/connecting-to-postgres sum] |
| Heroku | No free tier; in sustaining-engineering (maintenance) mode since 2026-02 | — | Avoid in new material. [third-party press, weak] |
| Cloud Run / AWS / Azure | Cloud Run has an always-free quota and scales to zero [memory] | Billing account, console complexity, bill-shock risk | Awareness: "what companies use"; best place to show real OIDC |

**Neon arithmetic to teach**: 0.25 CU awake all month = 0.25 × 730 ≈ 182 CU-hours > 100 free. Anything that touches the database at least every 5 minutes (an uptime monitor on a DB-backed URL, a platform health check on `/readyz`) keeps it awake and exhausts the allowance mid-month. Health checks and monitors must hit a DB-free `/healthz`.

## 9. Static hosting for a first website

- **GitHub Pages** [source: ghdocs raw]: on GitHub Free the repo must be public; site ≤1 GB; soft 100 GB/month bandwidth; soft 10 builds/hour (not applied to Actions deploys); deployments time out after 10 min; not for commercial/SaaS use or sensitive transactions; one user site (`<owner>.github.io`) plus one project site per repo (`<owner>.github.io/<repo>`); HTTPS automatic, also for custom domains. Two publishing modes: "Deploy from a branch" (simplest first deploy) or "GitHub Actions" (recommended when there is a build step).
- **Sub-path pitfall** [local]: Vite build emits `src="/assets/…"`; a project site lives under `/<repo>/`, so build with `vite build --base=/<repo>/` (output then has `src="/my-repo/assets/…"`). Plain HTML sites should use relative links.
- SPA deep links on Pages need a `404.html` copy of `index.html` [memory]. Serving the SPA from FastAPI avoids both problems: [local] `app.frontend("/", directory="dist")` returned the API JSON for `/api/hello`, `index.html` for `/` and for `/dashboard/settings` when the client accepts `text/html`, and 404 JSON for unknown paths requested as JSON.
- **Cloudflare**: use Workers static assets for new projects (`wrangler deploy`, `assets.directory`, `not_found_handling = "single-page-application"`) [source sum].

## 10. Domains, DNS and HTTPS basics

- Teach with free platform subdomains first (`*.github.io`, `*.fly.dev`, `*.onrender.com` all come with HTTPS). A custom domain is optional and costs roughly US$10–15/year for `.com` [memory].
- Records to know: A/AAAA (name → address), CNAME (alias), NS, TXT (verification), CAA (who may issue certificates), TTL. GitHub Pages: `www` → CNAME `<owner>.github.io`; apex → A `185.199.108–111.153` (+ AAAA `2606:50c0:8000–8003::153`) [source: ghdocs pages-https raw]. [local] DNS-over-HTTPS check: `curl -H 'accept: application/dns-json' 'https://cloudflare-dns.com/dns-query?name=octocat.github.io&type=A'` returned exactly those four addresses with TTL 3600; `dig` works on a normal Mac but is blocked in my sandbox.
- HTTPS: TLS certificate = proof of domain control signed by a CA; Let's Encrypt is free and automated (ACME). [local] `curl -sv https://letsencrypt.org/` showed `subject: CN=letsencrypt.org`, `start date: Nov 3 2026`, `expire date: Feb 1 2027`, `issuer: … Let's Encrypt; CN=YE2`, TLSv1.3. `curl -I http://github.com/` → `301` to https, and `strict-transport-security: max-age=31536000; includeSubdomains; preload`.
- Caddy [source: caddyserver.com/docs/automatic-https, quick-starts/reverse-proxy sum; reverse_proxy directive raw]: `app.example.com { reverse_proxy api:8000 }` is a complete HTTPS reverse proxy. Requirements: A/AAAA record points to the server, ports 80+443 reachable, persistent data directory. Default CAs: Let's Encrypt then ZeroSSL. Misconfiguration loops can hit CA rate limits — test with the staging CA. Lab files: `lab/shipit/deploy/vps/Caddyfile`, `compose.prod.yaml` (schema-validated, not run).
- Apex vs `www`, propagation delay (TTL), and "DNS changed but my laptop still sees the old value" are the classic confusions.

## 11. Environments, configuration and secrets

- Three environments: **dev** (laptop, SQLite or local Postgres, `.env`), **staging** (same image and config shape as prod, own database/branch), **prod**. One image is promoted; only environment variables differ. For a solo learner: run staging once to learn the idea (second Fly app + Neon branch), then keep prod + preview.
- Config from environment variables (12-factor III). [local] `pydantic-settings` with `env_prefix="SHIPIT_"`; `uv run --env-file file.env …` loads a file (`UV_ENV_FILE` also works) and **a real environment variable wins over the file** (`SHIPIT_ENV=prod` beat `staging` from the file).
- Rules: `.env` never committed (add it to `.gitignore` yourself — `uv init` does not [local]); commit `.env.example`; secrets live in the platform (`fly secrets set NAME=value` — redeploys unless `--stage` [source: fly docs raw]; Render environment variables; GitHub environment secrets); never in the image, in `fly.toml [env]`, in build args, or in logs; rotate on any leak; one deploy token per purpose, with an expiry (Fly's guide suggests `fly tokens create deploy -x 999999h` — teach a shorter expiry and a calendar reminder).
- Expose the running version: [local] `/healthz` returned `{'status': 'ok', 'version': '0.1.0', 'sha': 'abc1234', 'env': 'staging'}` with the SHA injected through `SHIPIT_GIT_SHA`.

## 12. Database migrations during deployment

[local] Alembic 1.20.1 on SQLite in the lab:
```
$ uv run alembic revision --autogenerate -m "create notes"   -> Detected added table 'notes'
$ uv run alembic upgrade head                                 -> Running upgrade  -> cccb03fe2de5, create notes
$ uv run alembic check                                        -> No new upgrade operations detected.
(change a model without a migration)
$ uv run alembic check   -> FAILED: New upgrade operations detected: [('add_column', None, 'notes', Column('tag', …))]   exit code 255
$ uv run alembic upgrade cccb03fe2de5:head --sql              -> ALTER TABLE notes ADD COLUMN tag VARCHAR(50);
$ uv run alembic downgrade -1 ; uv run alembic upgrade head   -> both ran; 2 existing rows preserved
```
- `migrations/env.py` reads the URL from settings (`config.set_main_option("sqlalchemy.url", get_settings().database_url)`), never from `alembic.ini`.
- **Lint trap** [local]: Alembic's generated files failed ruff 0.17.5's default rules (13 findings: UP007, I001, UP035, RUF100). Fix once by enabling the `post_write_hooks` ruff example already present (commented) in `alembic.ini`; verified: "Running post write hook 'ruff' … done".
- Where the migration runs:
  - Fly: `[deploy] release_command = "alembic upgrade head"` — executed once per deploy attempt in a throwaway Machine built from the new image, before any running Machine is created or updated; it has env and secrets but no volumes; 5-minute default timeout [source: docs.fly.io/reference/configuration raw].
  - Render: pre-deploy command (paid services only); on Free run `alembic upgrade head` as a CI step against the direct database URL, or in the start command [source raw].
  - Compose/VPS: one-off `migrate` service + `service_completed_successfully`.
- Rules to teach: migrations are reviewed code; apply automatically, forward only; make them backward compatible (**expand → deploy → contract**: add nullable column first, remove old things in a later release) so a code rollback never needs a schema rollback; use the **direct** (non-pooled) connection for migrations and dumps [source: Neon + Supabase docs]; before a risky migration create a Neon branch or a dump.

## 13. Backups and restore drills

- [local] Drill executed on SQLite (same five steps apply to Postgres): `sqlite3 dev.db ".backup 'backups/dev-<UTC>.db'"` → `pragma integrity_check` = `ok` → simulate disaster (`delete from notes` → 0 rows) → restore into a *new* file and verify (`2` rows, migration version `7d34b77e5117`) → only then switch. Record time taken (RTO) and backup age (RPO) in the handbook.
- Postgres commands [source: neon.com/docs/guides/backup-pg-dump raw]: `pg_dump -Fc -v -d "<direct connection string>" -f app.bak`; `pg_restore -v -d "<target connection string>" app.bak`; client major version should match the server; no local install needed: `docker run --rm postgres:18 pg_dump --version`.
- What "free" gives: Neon Free = 6 h instant restore + 1 snapshot (protection against "oops", not a backup policy); Render Free Postgres and Supabase Free = no backups. So the capstone needs a scheduled `pg_dump` (GitHub Actions `schedule:`) to private storage.
- Traps: scheduled workflows in public repos stop after 60 days without repo activity [source raw]; never upload database dumps as artifacts of a public repo [memory: artifacts follow repo visibility]; an untested backup is not a backup.

## 14. Logging, monitoring, alerting

- **Logs**: one JSON object per line on stdout; the platform collects them (`fly logs`, Render log stream). [local] sample: `{"ts": "2026-11-19T12:35:02.782+00:00", "level": "INFO", "logger": "shipit", "msg": "request", "request_id": "f4d4d20369bb", "method": "GET", "path": "/healthz", "status": 200, "duration_ms": 1.1}`. Never log secrets or full tokens.
- **Health**: `/healthz` (process alive, no DB) for platform checks and uptime monitors; `/readyz` (runs `SELECT 1`) for humans and deploy smoke tests. Fly check block: `[[http_service.checks]] method/path/interval/timeout/grace_period` [source raw].
- **Uptime**: UptimeRobot Free 50 monitors at 5-minute interval, 1 status page [source: uptimerobot.com/pricing sum]. Alternatives [memory]: Better Stack, healthchecks.io (for cron jobs such as the backup).
- **Errors**: Sentry Developer plan free — 1 user, 5k errors/month, 1 uptime monitor, email alerts [source: sentry.io/pricing sum]. [local] `sentry_sdk.init(dsn="")` creates no transport (nothing sent), and sentry-sdk 2.75.0 auto-detects `fastapi`, `starlette`, `sqlalchemy`, `logging` integrations; set `environment` and `release`.
- **Metrics/traces (awareness, now nearly free to demo)**: [local] `FastAPI(telemetry={"tracer_provider": …})` with an in-memory exporter produced a `GET /items/{item_id}` SERVER span with `http.request.method`, `http.response.status_code` (200 and 422), `http.route`, plus `fastapi.dependencies/endpoint/serialization` spans. Production switch: `FASTAPI_OTEL_AUTO_CONFIGURE=true`, `OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT` [source raw]. OpenTelemetry Python: traces and metrics Stable, logs "Development" [source: opentelemetry.io/status sum].
- **Alerting**: start with two alerts only — "site is down" and "new error type"; route to e-mail; write a one-page runbook ("what I check first").

## 15. Cost control, rollback, DORA

**Cost control**
- Prefer plans that cannot bill (no card on file): GitHub public repo, Neon Free, Render Free, Vercel Hobby, Cloudflare Free, FastAPI Cloud Hobby. GitHub blocks usage when included compute is consumed and no payment method exists [source raw].
- With a card on Fly: no billing alerts; keep one Machine (`fly deploy --ha=false` or `fly scale count 1`), `auto_stop_machines = "stop"`, `min_machines_running = 0`, no dedicated IPv4, no volumes unless needed, never create Managed Postgres by accident; stay in the personal organization (waiver applies only there).
- [local] The lab app peaked at ~100 MiB RSS in-process (macOS, app + test client), so 256 MB is feasible but tight; 512 MB is the safe size and still under $5 alone.
- Monthly ritual for the handbook: list every account, running app, database and domain; delete what is unused; check each dashboard's usage page.

**Rollback**
- Fly has no `rollback` command: `fly releases --image`, then `fly deploy --image registry.fly.io/<app>:deployment-…`; tag releases with `--image-label`; rollbacks do **not** undo config, secrets or migrations [source: docs.fly.io/blueprints/rollback-guide raw]. Strategies available: `rolling` (default), `canary`, `bluegreen`, `immediate` [source raw].
- Render: "Rollback" button reuses a retained build and disables auto-deploy until re-enabled [source raw]. Railway: rollback within image retention (24 h Free, 72 h Hobby) [source raw].
- Habit to teach first: **roll forward with `git revert`** through the normal pipeline; redeploy-previous-image is the emergency brake; database: never roll back schema in production, restore only for data loss.

**DORA (awareness)** [source: dora.dev/guides/dora-metrics sum, page dated 2026-01-05]
- Throughput: change lead time, deployment frequency, failed deployment recovery time. Instability: change fail rate, deployment rework rate.
- The learner can compute two from their own repo (deploys per week from the Actions history; commit-to-deploy time). The 2025 report's framing: AI amplifies whatever delivery practices a team already has [source: dora.dev/research sum].

## 16. Recommendation: one default path, one fallback

**Default — "one container on Fly.io + Neon"**
`git push` → GitHub Actions (ruff, pytest, `alembic check`) → `flyctl deploy` (remote build of the Dockerfile; `release_command` runs migrations) → one Fly Machine in `fra` with autostop → Neon Free Postgres in `aws-eu-central-1` (pooled URL for the app, direct URL for migrations/backups) → FastAPI serves `/api/*` and the built React app from the same origin → `/healthz` smoke test → Sentry + uptime monitor → tagged images also pushed to GHCR. (`fra` and `aws-eu-central-1` are example regions; pick the region nearest the learner and the users.)
Why: (1) every professional step is explicit and scriptable — build, migrate, release, verify, roll back; (2) real containers, so Docker lessons are used, not simulated; (3) $0 expected (bill < $5 waived; everything else free) with ~2 s cold starts instead of ~1 min; (4) same-origin deployment removes CORS and cross-site cookie problems from the first production deploy; (5) the example region, Frankfurt, exists on Fly, Render and Neon, so app and database sit together and the fallback keeps the same region (check the same for whichever region is chosen); (6) nothing is Fly-specific except `fly.toml` and one workflow step.
Costs/risks: credit card required (trial without card is unusable for a kept-alive app); no billing alerts; default HA creates 2 Machines; pricing policy has changed before — re-verify when Stage 8 is generated.

**Fallback — "same Dockerfile on Render Free + Neon"**
When there is no usable card, signup fails, or Fly's terms change. Same image definition, same database, same CI; Render auto-deploys "After CI Checks Pass"; migrations run as a CI step (or in the start command) because pre-deploy commands are paid; accept ~1 minute wake-up and 5 GB/month bandwidth. No card.

**Not chosen as default**: VPS (learner becomes responsible for a public server; ≥€5.5/month + domain) — keep as a one-week lab; Vercel/Netlify/Cloudflare (hide the container/ops layer; fine for front-end); Railway (account-age verification risk, $1/month free credit); Koyeb, Heroku (status above); FastAPI Cloud (beta, no DB) — good for a first deploy before Docker is taught.

## 17. Staged teaching order

Pull delivery forward ("deploy early, deploy often"); keep depth for Stage 8.

| Stage | Delivery/ops content | New idea for the learner |
|---|---|---|
| 1 | Publish one page with GitHub Pages ("Deploy from a branch") | repo → public URL; HTTPS exists |
| 3 | CI: Actions runs ruff + pytest on every PR; required check; Dependabot; pinning rule | "the robot checks my homework" |
| 4 | DNS and HTTPS by inspection (`dig`/DoH, `curl -v`); deploy the static site with the Pages Actions workflow (first OIDC contact); optional custom domain | names → addresses; certificates |
| 5 | Local Postgres from a provided `compose.yaml` ("Docker as an appliance"); env config + `.env.example`; Alembic; `/healthz`; first backend deploy without Docker (Render native runtime or FastAPI Cloud) + Neon | config vs code; migrations |
| 6 | `npm run build` → `dist/`; base-path pitfall; serve via `app.frontend()` | build artefact |
| 7 | Secrets, staging vs prod, same-origin vs CORS, auth secrets rotation | environments |
| 8 | In order: (1) Linux in a container; (2) images/containers/ports/volumes; (3) Dockerfile for the uv app + `.dockerignore` + non-root + lint; (4) layer cache + multi-stage; (5) Compose with Postgres, healthchecks, migrate service, watch; (6) registries: push to GHCR on a tag; (7) CD job: environments, secrets, concurrency, smoke test; (8) deploy on the default platform; (9) migrations in the pipeline + expand/contract; (10) logs, health, uptime, Sentry, OTel demo; (11) backup + restore drill; (12) rollback drill + short incident note + DORA numbers; (13) custom domain + HTTPS; (14) optional VPS lab with ssh, ufw, Compose + Caddy, systemd awareness, teardown; (15) cost and teardown checklist | operate what you ship |

Postpone to awareness only: Kubernetes, Terraform, multi-region, canary/blue-green mechanics, self-hosted runners, Nginx tuning, SLO math, OTel collectors, distroless/DHI, image signing, secret managers, cloud IAM.

Sensible defaults: Python 3.14 pinned in `.python-version` and the image tag; `compose.yaml`; port 8000; `/healthz` + `/readyz`; JSON logs on stdout; `SHIPIT_`-style env prefix; Postgres 18; the region nearest the learner and the users (the examples above use Frankfurt only as an example); one Machine with autostop; public capstone repo (free runners, environments, Pages, portfolio value).

## 18. Region accessibility

| Service | Mainland China status | Basis |
|---|---|---|
| `*.vercel.app` | Vercel's own guide: may be blocked or throttled; a custom domain is less likely to be affected but nothing is immune; Vercel gives no guarantee | [source: vercel.com/kb/guide/accessing-vercel-hosted-sites-from-mainland-china, updated 2026-09-11, sum] |
| Cloudflare `pages.dev` | Cloudflare's FAQ: Pages on `pages.dev` is not available in mainland China; `workers.dev` widely reported blocked | [source: developers.cloudflare.com/china-network/faq sum]; workers.dev [memory] |
| github.com / `*.github.io` | intermittent interference, slow; not dependable | third-party measurements (GreatFire) [weak] |
| Docker Hub | blocked/unreliable; public mirrors mostly shut since 2024-06; ghcr.io slow | third-party posts [weak] |
| Google services (Cloud Run `*.run.app`, Fonts, reCAPTCHA) | blocked | [memory] |
| `*.fly.dev`, `*.onrender.com`, `*.up.railway.app`, Neon, Supabase, Sentry | no reliable data found today; assume slow and unguaranteed | [memory] |
| PyPI / npm registry | reachable but slow; mirrors are the usual fix | [memory] |
| Hosting inside mainland China | needs ICP filing for a domain | [source: Vercel guide mentions ICP; rest memory] |

Guidance: do not assume the learner is, or is not, in mainland China; ask first. Put a 2-minute reachability check at the start of each deploy lesson (`curl -sS -o /dev/null -w '%{http_code}\n' https://<host>/`) and re-check payment-card acceptance for the chosen platform. If the audience for the capstone is in mainland China, none of the listed PaaS subdomains is dependable — use a custom domain at minimum and expect to need an in-country option.
Latency note: pick the region nearest the learner and the app's users; Africa/India egress costs 6× more on Fly.

## 19. Plain-Chinese analogies (ready to reuse)

- 镜像 image = 封好的预制菜/集装箱;容器 container = 加热上桌、正在运行的那一份;Dockerfile = 菜谱;registry = 中央仓库;`.dockerignore` = 搬家时"不带走清单";多阶段构建 = 厨房里做菜、只把菜端上桌,不把锅端上去;非 root 用户 = 给临时工只能进车间的门禁卡,而不是整栋楼的总钥匙。
- Compose = 一张总装图,一条命令同时启动应用、数据库和迁移任务;healthcheck = 开门营业前先确认后厨准备好了。
- CI = 每次交作业自动批改;CD = 批改通过后自动上架;environment secrets = 保险柜;OIDC = 当天有效的访客证,而不是长期钥匙;固定 SHA = 认准这一批次的货,而不是只看标签。
- DNS = 通讯录(名字查号码);A 记录 = 名字→门牌号;CNAME = "去问另一个名字";TTL = 通讯录多久刷新一次;证书 = 网站的身份证,CA = 发证机关,Let's Encrypt = 免费且自动续期的发证机关;Caddy = 自动帮你办证的前台;反向代理 = 总机转接。
- dev / staging / prod = 排练厅 / 彩排 / 正式演出;配置与密钥 = 同一出戏在不同剧场用不同的灯光和钥匙,剧本(代码)不变。
- 数据库迁移 = 按编号执行的装修施工单;expand → contract = 先开新门、大家都走新门之后再封旧门。
- 备份与恢复演练 = 消防演习:没演练过的备份等于没有备份;RPO = 最多丢多久的数据,RTO = 多久能恢复营业。
- 日志 = 航海日志;指标 = 仪表盘;追踪 trace = 快递单号上的每一站;uptime 监控 = 每五分钟有人来敲门;Sentry = 行车记录仪。
- 回滚 = 读取上一个存档;roll forward = 发一个修正补丁继续往前走。
- scale-to-zero 与冷启动 = 没客人就关灯省电,客人来了要等几秒开灯。
- 端口 = 大楼里的房间号;`127.0.0.1` = 只开内门,`0.0.0.0` = 对外开门;SIGTERM = 礼貌地请离场,SIGKILL = 强制清场;rwx = 读/写/执行三把钥匙 × 主人/同组/其他人;SSH 公钥 = 可以到处安装的锁,私钥 = 只在自己手里的钥匙;systemd = 物业管家(开机自启、挂了拉起)。
- DORA = 交付的体检指标:多快、多稳。

## 20. Beginner pitfalls (consolidated)

1. Copying `@v5`-style action references from old posts: `setup-uv@v10` does not exist; vendor docs also lag (Fly shows `checkout@v4`, `setup-flyctl@master`).
2. `uv sync --locked` fails in CI/Docker when `pyproject.toml` changed without `uv lock`: [local] "The lockfile at `uv.lock` needs to be updated, but `--locked` was provided." (exit 1). This is the desired safety net — teach the fix (`uv lock`, commit).
3. No `.dockerignore`: the host `.venv` (macOS binaries) lands in a Linux image; `.env` and `.git` leak into the image.
4. Server bound to `127.0.0.1` inside a container (unreachable) — `fastapi run` binds `0.0.0.0`, `fastapi dev` does not.
5. Shell-form `CMD` (no signal handling, slow stops); `:latest` tags; running as root.
6. Postgres 18 volume mounted at the old `/data` path; `depends_on` without a health condition; healthcheck using `curl` in a slim image; `$` vs `$$` in Compose healthcheck commands.
7. `postgres://` URLs (SQLAlchemy rejects the scheme); pooled URL used for migrations; forgetting `sslmode=require`.
8. Health check or uptime monitor that queries the database keeps Neon awake and burns the monthly CU-hours; on Render it also defeats spin-down (one always-awake free service fits in 750 h, two do not).
9. Secrets: committing `.env`; printing secrets in CI logs; putting secrets in `fly.toml [env]` or Docker `ARG/ENV`; long-lived deploy tokens; `authors` e-mail from `uv init` published in a public repo.
10. GitHub Free: private repo → no environment secrets/reviewers, no Pages, metered minutes.
11. Vite/SPA on a GitHub Pages project site without `--base`; SPA deep links 404.
12. Alembic: autogenerate accepted without reading; destructive migration deployed together with code that still needs the old column; generated files failing ruff.
13. Fly: 2 Machines by default; no billing alerts; trial Machines stop after 5 minutes; Managed Postgres at $38; rollback does not revert config or schema.
14. Render Free: 30-day Postgres expiry; no shell; no pre-deploy command; files written to disk vanish on restart (so no SQLite, no uploads).
15. Netlify credits consumed by frequent production deploys; Vercel/Cloudflare subdomains unreachable for mainland-China visitors.
16. Scheduled workflows silently disabled after 60 quiet days (backups stop); schedules drift at the top of the hour.
17. Believing "deployed" means "working": no smoke test, no log check, no alert.
18. macOS-only habits (`brew`, BSD flags) pasted into Linux servers and vice versa; practising Linux commands that do not exist on macOS.
19. Workspace inside iCloud-synced folders when Docker bind mounts start.
20. Forgetting to delete cloud resources after a lesson.

## 21. Source quality and unverified items

Read as **raw** text (strong): uv Docker and GitHub guides; `astral-sh/uv-docker-example`; `astral-sh/setup-uv` README and tags; GitHub Docs articles via `docs.github.com/api/article/body?pathname=…`; Fly docs via `docs.fly.io/<page>.md`; Render docs via `render.com/docs/<page>.md`; Railway plans via `docs.railway.com/pricing/plans.md`; Neon docs via `neon.com/docs/<page>.md`; FastAPI docs from `raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/…`; Docker docs from `raw.githubusercontent.com/docker/docs/main/content/…`; docker-library image docs and tag files; Vercel Hobby and FastAPI pages; Compose Specification schema. (Tip for builders: these Markdown endpoints are far more reliable for agents than rendered HTML.)
Read through a **summarising** fetch (re-check numbers before quoting): Docker best-practices, Docker Hub usage, Desktop release notes and licence, DHI, Compose releases; Railway/Koyeb/Supabase/Sentry/UptimeRobot/Netlify/FastAPI Cloud pricing pages; Cloudflare pricing, Pages limits, Pages banner, Python Workers, China FAQ; Vercel China guide; Caddy docs; Let's Encrypt posts; DORA pages; PostgreSQL versioning; OpenTelemetry status; Neon pooling; Supabase connection guide; Hetzner cloud page.

Not verified (do not present as fact without checking):
- The Dockerfile was never built and no container was run; `fly.toml` was never deployed; no workflow ran on GitHub; Compose files only schema-validated; the Caddyfile was not parsed by Caddy.
- Whether Render Free accepts the Docker runtime exactly as paid services do, whether Render Free needs a card, and Render paid prices (pricing page did not render).
- Exact Hetzner plan names/prices/availability after the 2026 increases; domain prices; which payment cards Fly/Hetzner accept in the learner's country.
- Mainland-China reachability of `fly.dev`, `onrender.com`, `up.railway.app`, `neon.tech`, `supabase.co`, `sentry.io`, `github.io` (no measurement available here); Docker Hub status in China (third-party only).
- Whether Fly health checks or monitor pings interact with autostop; exact failure semantics of a failing `release_command` (expected: deploy aborted).
- Google Cloud Run free quota, Heroku plan details, Better Stack/healthchecks.io free tiers, Fly volume snapshot retention, UptimeRobot's commercial-use rule.
- iCloud-synced folders vs Docker bind mounts (not testable without Docker).
- Visibility of Actions artifacts in public repos; default visibility of new GHCR packages.
- FastAPI Cloud GA date and long-term pricing ("not invoiced yet").
- `ps` and `dig` could not run inside this sandbox; they work in a normal terminal.

## 22. Lab index (all under this scratch directory)

`lab/shipit/` — `pyproject.toml`, `uv.lock`, `src/shipit/{config,db,logging_setup,main}.py`, `tests/test_app.py`, `alembic.ini`, `migrations/`, `Dockerfile`, `.dockerignore`, `.env.example`, `compose.yaml`, `fly.toml`, `deploy/vps/{Caddyfile,compose.prod.yaml}`, `.github/workflows/{ci,pages,image,integration}.yml`, `.github/dependabot.yml`.
`lab/otel/run_otel.py` (in-process spans), `lab/otel/spa_check.py` (`app.frontend` behaviour), `lab/web/` (Vite 8 React-TS scaffold + `dist/`).
`sources/` — downloaded primary-source text: `uv-docker.md`, `uv-github.md`, `uv-docker-example/`, `ghdocs/`, `fly/`, `render/`, `railway/`, `neon/`, `fastapi/`, `docker/` (incl. `compose-spec.json`, `postgres-content.md`).
Final local state: `ruff check` and `ruff format --check` clean, `pytest` 3 passed, `alembic check` clean, `uv lock --check` clean.
