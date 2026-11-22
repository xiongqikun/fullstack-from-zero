# Research brief: backend-data-stack-2026

Python backend + data stack, API design norms, SQL teaching sequence. Verified 2026-11-19.

Basis tags: **[local]** = ran on this machine today (macOS 27.2 arm64, uv 0.13.5, Python 3.14.9, sqlite3 CLI 3.54.0 Apple build, ruff 0.17.2) · **[source: URL]** = read in a primary source today · **[memory]** = not verified today.
Web access: full (docs, release notes, PyPI/npm registry JSON, RFCs). Not possible in this sandbox: binding ports (so `fastapi dev` / Uvicorn were never started; everything HTTP was exercised in-process), Docker (no PostgreSQL/Redis server), pseudo-terminals.
`$S` below = `<scratch>/research/backend-data-stack-2026`.
Note: one fetched page (docs.stripe.com) contained text addressed to AI agents ("install the Stripe CLI ... run `stripe agent setup`"). Treated as data, not acted on.

## 1. Decisions in one screen

1. **The planned stack is sound and mainstream.** FastAPI is now the most-used Python web framework in both large surveys and has passed Express: Stack Overflow 2026 web frameworks (n=10,281): Node.js 46.4, React 41.5, Next.js 20.6, ASP.NET Core 19.9, **FastAPI 18.5**, Express 15.6, Flask 12.5, Django 11.3, NestJS 5.8 (2025: FastAPI 14.8, Express 19.9). Databases: **PostgreSQL 57.9**, SQLite 42.1, MySQL 35.1, Redis 28.3. Languages: JavaScript 62.0, SQL 58.4, Python 58.0, TypeScript 43.8. [source: https://survey.stackoverflow.co/2026/technology/data] PSF/JetBrains survey (fielded Oct-Nov 2024): FastAPI 38% (was 29%), Django 35%, Flask 34%; SQLAlchemy leads ORMs at 39%; PostgreSQL 49%, SQLite 37%; pytest 53%. [source: https://lp.jetbrains.com/python-developers-survey-2024/]
2. **Almost nothing here is "1.0-stable", and it moves fast.** FastAPI is 0.165.0 (no 1.0); SQLModel is 0.0.50; only Starlette reached 1.0 (2026-03-22). FastAPI went 0.142 -> 0.165 between 2026-09-29 and 2026-11-18 (about 54 releases, 12 of them labelled "Breaking Changes"). [source: https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/release-notes.md] Consequence for the course: pin + commit `uv.lock`, stamp every lesson "verified with X.Y.Z", generate Stage 5+ just-in-time, and make auto-checkers assert behaviour, not framework output text.
3. **Default stack to teach (all verified working together today [local]):** Python 3.14 + uv -> `fastapi[standard]` 0.165.0 (Starlette 1.10.0, Pydantic 2.14.3, Uvicorn 0.54.0, fastapi-cli 0.0.34) -> SQLAlchemy 2.1.9 ORM (sync `Session`) -> Alembic 1.20.1 (pyproject template) -> SQLite first, then PostgreSQL 18 with psycopg 3.3.9 -> pytest 9.2.0 with the in-process `TestClient` -> pydantic-settings 2.16.3 -> PyJWT 2.15.1 + pwdlib 0.4.2 (argon2id) for auth.
4. **Teach SQL by hand in `sqlite3` before any ORM**, then Python `sqlite3` with parameters, then SQLAlchemy, then PostgreSQL. The 9-step sequence in the task is right but is missing two units: *writing data* (INSERT/UPDATE/DELETE) and *NULL*. All example queries are verified (section 11).
5. **Teach SQLAlchemy 2 + Pydantic explicitly, not SQLModel**, even though the FastAPI SQL tutorial uses SQLModel. SQLModel works today [local] but is 0.0.x, changed datetime semantics in 0.0.45 (2026-09-21), and merges "DB table" and "API schema" into one class, which hides the boundary the course wants to teach. Show SQLModel once so the learner can read the official docs.
6. **Sync first.** Plain `def` endpoints + sync `Session`. FastAPI docs: "If you just don't know, use normal `def`." [source: https://fastapi.tiangolo.com/async/] Async DB access is a later topic (SQLAlchemy 2.1 no longer installs greenlet by default).
7. **API norms worth putting in the handbook:** plural-noun resources, correct method/status semantics (RFC 9110), one error format (RFC 9457 `application/problem+json`; FastAPI has no built-in support, 60 lines of handlers verified here), pagination from day one, validate at the boundary with separate Create/Update/Read schemas, router -> service -> repository layering.
8. **Auth (Stage 7):** FastAPI docs now recommend PyJWT + `pwdlib[argon2]` (not python-jose + passlib). `passlib 1.7.4 + bcrypt 5.0.0` is broken on Python 3.14 [local]. OWASP: Argon2id first; do not keep tokens in `localStorage`; prefer HttpOnly cookies. OAuth 2.1 is still a draft (draft-17) and removes the password grant that the FastAPI tutorial is named after.

## 2. Versions today

| Component | Version today | Released | What matters | Basis |
|---|---|---|---|---|
| FastAPI | 0.165.0 | 2026-11-18 | Python >=3.11; needs starlette>=1.6.0, pydantic>=2.9.0; no 1.0 | [local] + [source: https://pypi.org/pypi/fastapi/json] |
| Starlette | 1.10.0 | 2026-10-24 | 1.0.0 on 2026-03-22 removed `on_event`, `on_startup`, `@app.route`; Python >=3.11 since 1.8.0 | [local] + [source: https://starlette.dev/release-notes/] |
| Pydantic | 2.14.3 | 2026-11-04 | still major 2; no v3 announced in the changelog; 2.14.0 dropped Python 3.9 | [local] + [source: https://pydantic.dev/docs/validation/latest/get-started/changelog/] |
| pydantic-settings | 2.16.3 | 2026-11-13 | pulls in python-dotenv itself | [local] |
| Uvicorn | 0.54.0 | 2026-09-24 | experimental HTTP/2 via `zttp`; `fastapi dev/run` wrap it | [local] + [source: https://uvicorn.dev/release-notes/] |
| fastapi-cli / fastapi-cloud-cli | 0.0.34 / 0.28.0 | | commands: dev, run, login, deploy, cloud | [local] |
| SQLAlchemy | 2.1.9 (2.0.58 still maintained) | 2026-11-16 | Python >=3.11; `postgresql://` now means psycopg 3; greenlet only via `[asyncio]` extra | [local] + [source: https://docs.sqlalchemy.org/en/21/changelog/migration_21.html] |
| Alembic | 1.20.1 | 2026-10-22 | templates: generic, pyproject, async, pyproject_async, multidb; `alembic check` | [local] |
| SQLModel | 0.0.50 | 2026-11-13 | still 0.0.x; SQLAlchemy 2.1 support since 0.0.48; UTC datetimes by default since 0.0.45 (breaking) | [local] + [source: https://sqlmodel.tiangolo.com/release-notes/] |
| psycopg (v3) | 3.3.9 (bundled libpq 18.6) | 2026-11-12 | `uv add "psycopg[binary]"`; arm64/py3.14 wheel installs; docs list PostgreSQL 10-18 | [local] + [source: https://www.psycopg.org/psycopg3/docs/basic/install.html] |
| psycopg2 | 2.9.13 | 2026-09-09 | what old tutorials install; no longer SQLAlchemy's default | [source: https://pypi.org/pypi/psycopg2/json] |
| PostgreSQL | 18.7 current; 19 RC 2 | 2026-11-12 | **19 GA is planned for 2026-11-19 (today)**; at 12:34 UTC the versions feed still listed 18 as current; 14 is now EOL | [source: https://www.postgresql.org/versions.json, https://www.postgresql.org/about/news/postgresql-187-1712-1616-1520-1425-and-19-rc-2-released-3442/] |
| SQLite | CLI 3.54.0 (Apple); Python 3.14.9 `sqlite3` module links 3.53.1 | | FK enforcement off, double-quoted strings accepted (Apple build `DQS=3`) | [local] |
| httpx | 0.28.1 | 2024-12-06 | no release for almost two years | [source: https://pypi.org/pypi/httpx/json] |
| httpx2 | 2.16.2 | 2026-11-16 | Pydantic-maintained continuation, `import httpx2`; what Starlette's TestClient now uses | [local] + [source: https://github.com/pydantic/httpx2] |
| pytest | 9.2.0 | 2026-10-27 | anyio plugin (4.16.0) arrives with FastAPI, enough for async tests | [local] |
| PyJWT / pwdlib / argon2-cffi | 2.15.1 / 0.4.2 / 25.1.0 | | the pair the FastAPI docs use | [local] |
| passlib / python-jose | 1.7.4 (2020-10-08) / 3.5.0 (2025-05-28) | | old-tutorial pair; passlib+bcrypt 5 fails on 3.14 | [local] |
| OpenAPI | FastAPI emits 3.1.0; spec latest is 3.2.1 (2026-09-10) | | client generators must support 3.1 | [local] + [source: https://spec.openapis.org/oas/latest.html] |
| Redis / Valkey | 8.10.3 / 9.1.4 | Oct 26 (page shows no year) / 2026-11-18 | Redis >=8 is RSALv2/SSPLv1/AGPLv3; Valkey is the BSD fork under the Linux Foundation | [source: https://github.com/redis/redis/releases, https://redis.io/legal/licenses/, https://valkey.io/] |
| Job queues | Celery 5.7.0, RQ 3.0.0, Dramatiq 2.2.1, arq 0.28.0, taskiq 0.13.0 | | awareness only | [source: pypi.org JSON] |
| Alternatives | Django 6.1.3 (py>=3.12), Flask 3.1.3, DRF 3.18.3, django-ninja 1.8.0, Litestar 2.25.0; Express 5.3.0, NestJS 12.5.1, Hono 4.13.19, Fastify 5.12.8, Next.js 16.4.6 | | | [source: pypi.org / registry.npmjs.org JSON] |

## 3. What changed compared with older tutorials

| Older tutorial says | Today | Basis |
|---|---|---|
| `pip install fastapi uvicorn`, `uvicorn main:app --reload` | Official docs: `uv init awesome-project --bare`, `uv add "fastapi[standard]"`, `uv run fastapi dev`; production `fastapi run`. `fastapi dev` listens on 127.0.0.1 with reload; `fastapi run` on 0.0.0.0 without reload | [source: https://fastapi.tiangolo.com/tutorial/, https://fastapi.tiangolo.com/fastapi-cli/] + [local] `--help` |
| pass the file path every time | `[tool.fastapi] entrypoint = "pkg.main:app"` in pyproject.toml is the recommended way (the VS Code extension and FastAPI Cloud read it); auto-discovery tries main.py, app.py, api.py, app/main.py | [source: same] + [local] resolved in-process |
| Python 3.8/3.9/3.10 | FastAPI requires >=3.11 (3.8 dropped 0.125.0 2025-12-17, 3.9 dropped 0.129.0 2026-02-12, 3.10 dropped 0.162.6 2026-11-13). SQLAlchemy 2.1, Starlette, SQLModel, pwdlib, httpx2 also need >=3.11 | [source: release notes, PyPI JSON] |
| Pydantic v1 (`.dict()`, `orm_mode`, `@validator`, `from pydantic import BaseSettings`) | FastAPI dropped Pydantic v1 (0.126.0-0.128.0, Dec 2025). Old names still run but warn `PydanticDeprecatedSince20`; `BaseSettings` import raises `PydanticImportError` (moved to `pydantic-settings`). Use `.model_dump()`, `ConfigDict(from_attributes=True)`, `@field_validator` | [local] |
| `@app.on_event("startup")` | Deprecated: emits `DeprecationWarning` in 0.165.0; use `lifespan`. Starlette 1.0 removed it; FastAPI re-implements it. **The official SQL tutorial code still uses `on_event`** (`docs_src/sql_databases/tutorial001.py` line 35) | [local] + [source: https://fastapi.tiangolo.com/advanced/events/, raw GitHub docs_src] |
| `uv add httpx` / `pip install httpx` for tests | Starlette's TestClient is "built on `httpx2`"; plain httpx "still supported, but deprecated". `fastapi[standard]` installs both. Bare `fastapi` + `httpx` -> `StarletteDeprecationWarning`; neither -> `RuntimeError ... requires the httpx2 package`. The FastAPI testing page still says `uv add httpx` | [local] + [source: https://starlette.dev/testclient/, https://fastapi.tiangolo.com/tutorial/testing/] |
| any Content-Type works for JSON bodies | 0.132.0 (2026-02-23): strict Content-Type check. JSON sent as `text/plain` or with no Content-Type -> 422. `curl -d` sends form encoding [memory]: use `curl --json` (curl 8.7.1 here has it) | [source: release notes] + [local] |
| `python-jose` + `passlib[bcrypt]` | Docs: `uv add pyjwt`, `uv add "pwdlib[argon2]"`, `PasswordHash.recommended()`, a dummy-hash check against timing attacks, `datetime.now(UTC)` | [source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/] + [local] |
| missing credentials -> 403 | security classes return 401 since 0.122.0 (2025-11-24) | [source: release notes] |
| `ORJSONResponse` for speed | deprecated in 0.131.0; since 0.130.0 responses with a return type / response model are serialized by Pydantic's Rust core | [source: release notes] |
| `StaticFiles` + catch-all route to serve a SPA | `app.frontend("/", directory="dist", fallback="index.html")` since 0.138.0 (2026-06-20); API routes win, HTML navigations fall back to index.html, missing assets 404 | [source: https://fastapi.tiangolo.com/tutorial/frontend/] + [local] |
| `status.HTTP_422_UNPROCESSABLE_ENTITY` | deprecated alias; `HTTP_422_UNPROCESSABLE_CONTENT` (RFC 9110 name "Unprocessable Content") | [local] |
| `postgresql://` + `psycopg2-binary` | SQLAlchemy 2.1: `postgresql://` resolves to driver `psycopg` (v3). Install `psycopg[binary]`; write `postgresql+psycopg://` to be explicit | [local] `create_engine(...).dialect.driver` |
| `declarative_base()`, `Column(...)`, `session.query()`, `engine.execute()` | `class Base(DeclarativeBase)`, `Mapped[...]` + `mapped_column()`, `select()` + `session.scalars()`. Old ORM style still runs with `LegacyAPIWarning`/`MovedIn20Warning`; `engine.execute` and raw-string `conn.execute("...")` raise errors | [local] |
| `alembic init alembic` + big alembic.ini | `alembic init --template pyproject migrations` writes `[tool.alembic]` into pyproject.toml (a small alembic.ini remains for URL + logging) | [local] |
| Docker volume at `/var/lib/postgresql/data` | For the `postgres` image 18+, PGDATA is `/var/lib/postgresql/18/docker` and the volume is `/var/lib/postgresql`; `latest` = 18.7 today and will become 19 | [source: https://hub.docker.com/_/postgres] |
| "Redis is BSD" | 7.4-7.8 RSALv2/SSPLv1; >=8.0 adds AGPLv3; Valkey is the BSD line | [source: https://redis.io/legal/licenses/] |
| `uv init` creates a flat `hello.py`/`main.py` | uv 0.13.5: plain `uv init x` and `uv init --app x` create a packaged `src/x/__init__.py` layout with `[build-system] uv_build` and `[project.scripts]`; `--no-package` gives flat `main.py`; `--bare` gives only pyproject.toml. It also copies the git user name/email into `authors` (`--author-from none` avoids that) | [local] |

Other recent FastAPI additions (awareness only): dependency scopes `Depends(..., scope="function"|"request")` 0.121.0; JSON Lines and SSE streaming 0.134.0/0.135.0; native OpenTelemetry 0.142.0 (exporter opt-in since 0.143.0); `Depends(max_concurrency=...)` 0.163.0; `FastAPI(max_body_size=...)` 0.164.0 and `form_limits=` 0.165.0. [source: release notes] + [local] `inspect.signature`.

## 4. Verified build A: the official quick start (flat, for the first lesson)

```bash
export UV_CACHE_DIR="$TMPDIR/uv-cache"            # sandbox only
uv init awesome-project --bare --python 3.14      # creates only pyproject.toml
cd awesome-project
uv add "fastapi[standard]"                        # 59 packages (bare "fastapi" = 11; "standard-no-fastapi-cloud-cli" = 53)
uv add --dev pytest
# write main.py and test_main.py (below)
uv run pytest -q                                  # -> 2 passed in 0.55s
uv run fastapi dev                                # NOT run here (ports blocked); auto-discovery resolved "main:app" in-process
```

```python
# main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

```python
# test_main.py  (no server, no port: the client calls the app in-process)
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_item_validation():
    assert client.get("/items/42?q=hi").json() == {"item_id": 42, "q": "hi"}
    assert client.get("/items/abc").status_code == 422
```

Note: without `--python 3.14`, `uv init` in this sandbox shell picked Python 3.12 (`requires-python = ">=3.12"`) because the only Python in uv's default managed directory is 3.12.15; pass `--python` explicitly in lesson commands. [local] Files: `$S/probe/awesome-project/`.

## 5. Verified build B: engineering layout (router / service / repository, SQLAlchemy 2, Alembic, pytest)

Project: `$S/notes-api/` (about 520 lines incl. tests; `ruff check` and `ruff format --check` clean with ruff 0.17.2 defaults; `pytest -W error` -> **12 passed in 0.49s**). [local]

### 5.1 Commands, in the order they were run

```bash
uv init --app --vcs none --python 3.14 notes-api && cd notes-api   # src/notes_api/ package layout
uv add "fastapi[standard]" sqlalchemy alembic
uv add --dev pytest
uv add "psycopg[binary]" pyjwt "pwdlib[argon2]"                    # later steps
# removed the generated [project.scripts] entry; wrote the files in 5.2
uv run alembic init --template pyproject migrations
# edited migrations/env.py (5.3)
uv run alembic revision --autogenerate -m "create notes table"
uv run alembic upgrade head
uv run alembic current        # -> 033973f09ead (head)
uv run alembic check          # -> "No new upgrade operations detected."  exit 0
uv run pytest -q
```

In the sandbox every `uv run ...` after the installs was typed as `uv run --no-sync ...` (to avoid a network re-sync); learners use plain `uv run`. Installed set recorded by `uv add`: fastapi 0.165.0, starlette 1.10.0, pydantic 2.14.3 (pydantic-core 2.50.4), pydantic-settings 2.16.3, uvicorn 0.54.0, sqlalchemy 2.1.9, alembic 1.20.1 (+ mako 1.4.3), httpx 0.28.1, httpx2 2.16.2, anyio 4.16.0, python-multipart 0.0.34, typer 0.29.2, fastapi-cli 0.0.34, fastapi-cloud-cli 0.28.0 (which brings sentry-sdk, rignore, agent-detector, detect-installer), opentelemetry-api/sdk 1.45.2, pytest 9.2.0.

### 5.2 Layout and the load-bearing code

```
notes-api/
  pyproject.toml            # deps, [tool.alembic], [tool.fastapi] entrypoint, [tool.pytest.ini_options]
  alembic.ini               # only URL placeholder + logging
  migrations/env.py, migrations/versions/*.py
  src/notes_api/
    config.py               # Settings(BaseSettings): NOTES_DATABASE_URL, .env
    db.py                   # Base + naming convention, make_engine(), get_session(), SessionDep
    models.py               # SQLAlchemy tables (Note)
    schemas.py              # Pydantic: NoteCreate / NoteUpdate / NoteRead / NotePage
    repository.py           # the only module that talks to the ORM
    service.py              # business rules, transaction boundary, domain exceptions
    routers/notes.py        # HTTP in/out, status codes
    errors.py               # RFC 9457 problem+json handlers
    main.py                 # FastAPI(), include_router(prefix="/api/v1")
  tests/conftest.py, test_notes.py, test_async.py, test_migrations.py
```

pyproject.toml additions: `[tool.fastapi]` with `entrypoint = "notes_api.main:app"` and `[tool.pytest.ini_options]` with `testpaths = ["tests"]`.

```python
# db.py (core)
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def make_engine(url: str, **kwargs: Any) -> Engine:
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args, **kwargs)
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _enable_sqlite_foreign_keys(dbapi_connection, _record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = make_engine(get_settings().database_url)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:   # one session per request
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
```

```python
# models.py: the database table
class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), unique=True)
    body: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    archived: Mapped[bool] = mapped_column(server_default=false())


# schemas.py: what may cross the HTTP boundary (also NoteUpdate, NotePage)
class NoteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")   # unknown fields such as "is_admin" -> 422

    title: str = Field(min_length=1, max_length=200)
    body: str = ""


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # can be built from an ORM object

    id: int
    title: str
    body: str
    created_at: datetime
```

```python
# routers/notes.py (excerpt): HTTP only
router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(data: NoteCreate, session: SessionDep, response: Response):
    note = service.create_note(session, data)
    response.headers["Location"] = f"/api/v1/notes/{note.id}"
    return note


@router.get("", response_model=NotePage)
def list_notes(session: SessionDep, limit: Annotated[int, Query(ge=1, le=100)] = 20,
               offset: Annotated[int, Query(ge=0)] = 0):
    items, total = service.list_notes(session, limit=limit, offset=offset)
    return {"items": items, "total": total, "limit": limit, "offset": offset}
```

```python
# service.py (excerpt): business rule + transaction boundary, no HTTP imports
def create_note(session: Session, data: NoteCreate) -> Note:
    if repository.get_by_title(session, data.title) is not None:
        raise DuplicateTitleError(data.title)
    note = repository.add(session, Note(**data.model_dump()))
    session.commit()
    session.refresh(note)
    return note


# repository.py (excerpt): the only module that touches the ORM
def add(session: Session, note: Note) -> Note:
    session.add(note)
    session.flush()  # sends INSERT, fills note.id, does NOT commit
    return note
```

```python
# errors.py (core): one error format for the whole API. Handlers are registered with @app.exception_handler for
# NoteNotFoundError -> 404, DuplicateTitleError -> 409, StarletteHTTPException (unknown URL, wrong method,
# any HTTPException) and RequestValidationError -> 422 plus an "errors" list.
def problem(request: Request, status: int, detail: str, **extensions: object) -> JSONResponse:
    body = {"type": "about:blank", "title": HTTPStatus(status).phrase, "status": status,
            "detail": detail, "instance": request.url.path, **extensions}
    return JSONResponse(body, status_code=status, media_type="application/problem+json")
```

Real output for `POST /api/v1/notes {"title": "", "extra": 1}` [local]:

```json
{"type": "about:blank", "title": "Unprocessable Content", "status": 422,
 "detail": "The request is not valid.", "instance": "/api/v1/notes",
 "errors": [{"pointer": "/body/title", "detail": "String should have at least 1 character"},
            {"pointer": "/body/extra", "detail": "Extra inputs are not permitted"}]}
```

Without those handlers FastAPI answers `{"detail": [{"type": "string_too_short", "loc": ["body", "title"], "msg": ..., "input": "", "ctx": {...}}]}` as `application/json`, and unknown URLs give `{"detail": "Not Found"}`. [local] The FastAPI error-handling page does not mention RFC 9457. [source: https://fastapi.tiangolo.com/tutorial/handling-errors/] Caveat: after overriding handlers, `/openapi.json` still documents 422 as `HTTPValidationError` unless you declare `responses={422: {"model": Problem}}` on the router (verified: the default schema is then replaced). [local]

### 5.3 Alembic: exact edits and outputs

`alembic init --template pyproject migrations` created `migrations/env.py`, `script.py.mako`, `README`, a small `alembic.ini`, and appended `[tool.alembic]` (with `script_location = "%(here)s/migrations"`, `prepend_sys_path = ["."]`) to pyproject.toml. Two edits to `env.py`:

```python
from notes_api import models  # noqa: F401  (import so tables register on Base.metadata)
from notes_api.config import get_settings
from notes_api.db import Base

config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata
...
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=connection.dialect.name == "sqlite",
        )
```

```text
$ uv run alembic revision --autogenerate -m "create notes table"
INFO  [alembic.autogenerate.compare.tables] Detected added table 'notes'
  Generating .../migrations/versions/033973f09ead_create_notes_table.py ...  done
$ uv run alembic upgrade head
INFO  [alembic.runtime.migration] Running upgrade  -> 033973f09ead, create notes table
$ sqlite3 notes.db ".schema notes"
CREATE TABLE notes (
	id INTEGER NOT NULL,
	title VARCHAR(200) NOT NULL,
	body TEXT NOT NULL,
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
	CONSTRAINT pk_notes PRIMARY KEY (id),
	CONSTRAINT uq_notes_title UNIQUE (title)
);
```

Second migration (added `archived` to the model): `alembic check` then printed `FAILED: New upgrade operations detected: [('add_column', None, 'notes', Column('archived', Boolean() ...` with exit code 255 (also 255 with `Target database is not up to date.` when the database is behind head); autogenerate produced `with op.batch_alter_table('notes') as batch_op: batch_op.add_column(sa.Column('archived', sa.Boolean(), server_default=sa.text('0'), nullable=False))`; `alembic upgrade head`, `alembic downgrade -1`, `alembic upgrade head` all worked. [local]

Findings from this run [local]:
- Without the naming convention the first autogenerate emitted an unnamed `sa.UniqueConstraint('title')`. Alembic docs: autogenerate cannot detect "Anonymously named constraints", nor table/column renames, and "It is always necessary to manually review and correct the candidate migrations". [source: https://alembic.sqlalchemy.org/en/latest/autogenerate.html]
- **Migrations generated against SQLite are not portable.** Rendering the same two revisions for PostgreSQL offline (`NOTES_DATABASE_URL=postgresql+psycopg://... uv run alembic upgrade head --sql`, no server needed) printed `ALTER TABLE notes ADD COLUMN archived BOOLEAN DEFAULT 0 NOT NULL;` (the SQLite-flavoured default `0` was frozen into the script; PostgreSQL rejects an integer default on a boolean column [memory]), plus `id SERIAL` and `created_at TIMESTAMP WITHOUT TIME ZONE`. When the course moves to PostgreSQL, regenerate migrations against PostgreSQL.
- `render_as_batch=True` is needed because SQLite "has almost no support for the ALTER statement"; Alembic copies the table. "This mode is safe to use in all cases." [source: https://alembic.sqlalchemy.org/en/latest/batch.html]
- Alembic's `script.py.mako` generates `from typing import Sequence, Union`; ruff 0.17.2 defaults flag it (UP007, UP035, I001). Either enable the ruff `post_write_hooks` that the pyproject template ships commented out, or run `ruff check --fix` on new revisions.
- A migration smoke test runs Alembic from pytest: `cfg = Config("alembic.ini", toml_file="pyproject.toml"); command.upgrade(cfg, "head"); command.check(cfg); command.downgrade(cfg, "base")` (`$S/notes-api/tests/test_migrations.py`).

### 5.4 Test setup that works

```python
# tests/conftest.py
@pytest.fixture
def session() -> Iterator[Session]:
    engine = make_engine("sqlite://", poolclass=StaticPool)   # fresh in-memory DB per test
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)
    with TestSession() as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
```

- `StaticPool` is required for `sqlite://` in-memory, otherwise each connection sees its own empty database. [local]
- `TestClient(app)` returns `httpx2.Response` objects here. [local]
- Lifespan runs only inside `with TestClient(app) as client:`; a bare `TestClient(app)` skipped startup/shutdown. [local] + [source: https://starlette.dev/testclient/]
- Async variant passes too: `@pytest.mark.anyio` + `httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app), base_url="http://test")` with an `anyio_backend` fixture returning `"asyncio"`; legacy `httpx.ASGITransport` also still works. The FastAPI async-tests page uses `from httpx import ASGITransport, AsyncClient` and warns that `AsyncClient` does not trigger lifespan. [local] + [source: https://fastapi.tiangolo.com/advanced/async-tests/]
- Under `pytest -W error` on Python 3.14, an engine that is never `dispose()`d fails a later test with `ResourceWarning: unclosed database in <sqlite3.Connection ...>`. [local]

### 5.5 Behaviours observed in-process (good lesson material) [local]

- `GET /items/` when the route is `/items` -> `307` redirect to `/items`.
- With `/users/me` declared before `/users/{user_id}`, `/users/me` matched its own function and `GET /users/abc` gave 422, not 404 (declared the other way round, "me" would be parsed as a user_id [memory]).
- Wrong method -> 405, but the `Allow` header listed only `POST` for a path that has GET and POST (each path operation is a separate route).
- CORS: preflight from an allowed origin -> 200 with `access-control-allow-*` headers; from another origin -> `400 Disallowed CORS origin`; a simple GET from a disallowed origin **still returns 200 with the data**, only without the allow header. CORS is a browser rule, not server-side access control. Defaults: `allow_methods=('GET',)`, `allow_credentials=False`, `max_age=600`. "None of allow_origins, allow_methods and allow_headers can be set to ['*'] if allow_credentials is set to True." [source: https://fastapi.tiangolo.com/tutorial/cors/]
- Timestamps: the API returned `"created_at": "2026-11-19T12:36:49"` with no UTC offset; on SQLite even `DateTime(timezone=True)` comes back naive. PostgreSQL `timestamptz` behaves differently [memory]. SQLModel 0.0.45 added a `UTCDateTime` type for this. [local] + [source: https://sqlmodel.tiangolo.com/release-notes/]
- ORM: looping over 5 authors and touching `.books` issued 6 SELECTs (N+1); `select(Author).options(selectinload(Author.books))` issued 2. `with Session(engine) as session, session.begin():` committed on success and rolled back on an exception.

## 6. FastAPI facts for lesson writers

- **Bigger applications** (official): package `app/` with `main.py`, `dependencies.py`, `routers/items.py`, `routers/users.py`, `internal/admin.py`; `router = APIRouter(prefix="/items", tags=["items"], dependencies=[...], responses={404: {...}})`; `app.include_router(users.router)`; import the submodules (`from .routers import items, users`), not `router` objects; prefix must not end with `/`; run with `uv run fastapi dev` after setting `[tool.fastapi] entrypoint = "app.main:app"`. [source: https://fastapi.tiangolo.com/tutorial/bigger-applications/] The docs stop at routers + dependencies; service/repository layering is a community convention, not an official rule.
- **Settings**: `uv add pydantic-settings`; `class Settings(BaseSettings)` with `model_config = SettingsConfigDict(env_file=".env")`; expose through `@lru_cache def get_settings()` and `Annotated[Settings, Depends(get_settings)]`; override in tests through `app.dependency_overrides`. Env names are matched case-insensitively. [source: https://fastapi.tiangolo.com/advanced/settings/] Verified with `env_prefix="NOTES_"`; note `get_settings.cache_clear()` is needed when a test changes the environment. [local]
- **Dependencies with yield**: exit code runs after the response is sent by default (`scope="request"`); `scope="function"` ends before the response. [source: https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/]
- **Response models**: a return type or `response_model` filters output ("particularly important for security"); prefer the return annotation, use `response_model` when the returned object is a different type (ORM object -> schema). [source: https://fastapi.tiangolo.com/tutorial/response-model/]
- **Versioning policy**: "any version below 1.0.0 could potentially add breaking changes"; breaking changes land in MINOR, bug fixes in PATCH; pin e.g. `fastapi[standard]>=0.112.0,<0.113.0`; do not pin Starlette. [source: https://fastapi.tiangolo.com/deployment/versions/]
- **Typed front-end client**: `npx @hey-api/openapi-ts -i http://localhost:8000/openapi.json -o src/client`; "FastAPI automatically generates OpenAPI 3.1 specifications, so any tool you use must support this version." [source: https://fastapi.tiangolo.com/advanced/generate-clients/]
- **Reference implementation of the whole plan**: `fastapi/full-stack-fastapi-template` (46.3k stars): FastAPI, SQLModel, Pydantic, PostgreSQL, React + TypeScript + Vite, Tailwind + shadcn/ui, generated client, Playwright, pytest, Docker Compose, Traefik, GitHub Actions, JWT, "Secure password hashing by default". [source: https://github.com/fastapi/full-stack-fastapi-template]
- **Background work**: `BackgroundTasks` for small in-process jobs; "bigger tools like Celery" with "RabbitMQ or Redis" for heavy or multi-server work. [source: https://fastapi.tiangolo.com/tutorial/background-tasks/]
- **Chinese docs** exist at https://fastapi.tiangolo.com/zh/ and state "本翻译由人类引导的 AI 生成"; same uv commands as English. SQLModel has no Chinese docs (404). [source + local curl]

## 7. Data layer facts

- **SQLAlchemy 2.1** (the current release series; 2.0.x gets maintenance releases; 2.1.0's own release date was not checked): psycopg 3 is the default PostgreSQL driver; greenlet not installed by default; `Select[int, str]` typing; `filter_by()` ambiguity errors; dataclass default changes. [source: https://docs.sqlalchemy.org/en/21/changelog/migration_21.html] The Unified Tutorial order (Engine -> Transactions -> Metadata -> Data -> ORM -> Related objects) is a good outline. [source: https://docs.sqlalchemy.org/en/21/tutorial/index.html]
- **SQLModel**: the official FastAPI SQL tutorial code (lifespan instead of `on_event`) passes under `-W error` with sqlmodel 0.0.50 + SQLAlchemy 2.1.9 + Pydantic 2.14.3 (`$S/probe/sqlmodel-probe`). Docs: "SQLModel will have migration utilities wrapping Alembic, but for now, you can use Alembic directly." [local] + [source: https://fastapi.tiangolo.com/tutorial/sql-databases/]
- **PostgreSQL 18** (2025-09-25): async I/O, `uuidv7()`, virtual generated columns by default, OAuth authentication, `OLD`/`NEW` in `RETURNING`, skip scan; MD5 passwords deprecated. [source: https://www.postgresql.org/docs/18/release-18.html] Local install options on macOS: Docker `postgres:18` (machine has Docker Desktop, no `psql`), Homebrew `postgresql@18` 18.7 (keg-only, arm64 bottles), Postgres.app. [source: https://hub.docker.com/_/postgres, https://formulae.brew.sh/api/formula/postgresql@18.json, https://postgresapp.com/]
- **When SQLite is enough** (official): fine for sites under about 100K hits/day, one writer at a time; choose client/server when data is separated from the app by a network, many concurrent writers, or big data; "SQLite makes a good database engine for use in teaching SQL." [source: https://www.sqlite.org/whentouse.html]
- **SQLite quirks verified on this Mac** [local]: `PRAGMA foreign_keys` returns 0 (an orphan row was inserted without error until `PRAGMA foreign_keys = ON`); a non-STRICT `INTEGER` column stored `'abc'` as text while a `STRICT` table refused it; `SELECT "hello"` returns the string hello (`.dbconfig` shows `dqs_dml on`, although upstream disabled this in the CLI since 3.41 [source: https://www.sqlite.org/quirks.html]); `TRUE` is integer 1; dates are text; `price NUMERIC` showed 28.00 as 28 and `0.1 + 0.2 = 0.30000000000000004`; `LIKE 'animal%'` matched "Animal Farm"; a bare column in `GROUP BY` is accepted; a failed statement inside `BEGIN ... COMMIT` did **not** abort the transaction (the first half of a transfer was committed: balance 80 -> 580).
- **Files and sync**: backup/sync tools copying a database mid-transaction, or separating it from its `-journal`/`-wal` file, can corrupt it. [source: https://www.sqlite.org/howtocorrupt.html] If the learner's folders are in an iCloud-synced folder (for example a synced Desktop), keep `.db` files (and `.venv`) out of it. The page does not name iCloud; this is an inference.
- **Redis / jobs**: awareness only until a real need (caching, rate limiting, queues). Django 6.0 added a Tasks framework but "does not provide a worker mechanism". [source: https://docs.djangoproject.com/en/6.0/releases/6.0/]

## 8. Authentication: what to teach

- **Hashing**: OWASP: "Use Argon2id with a minimum configuration of 19 MiB of memory, an iteration count of 2, and 1 degree of parallelism"; bcrypt only "for legacy systems" (72-byte limit); PBKDF2-HMAC-SHA256 at 600,000 iterations for FIPS. [source: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html] pwdlib default here: `$argon2id$v=19$m=65536,t=3,p=4$...` (97 chars, about 23 ms per hash); same password hashed twice gives different strings; `verify_and_update` returns `(True, None)`. [local]
- **JWT** with PyJWT [local]: `jwt.encode({"sub": "42", "exp": datetime.now(UTC) + timedelta(minutes=30)}, SECRET, algorithm="HS256")`; `jwt.decode(token, SECRET, algorithms=["HS256"])`; expired -> `ExpiredSignatureError: Signature has expired`; wrong key -> `InvalidSignatureError`. The payload is only base64: decoded without the key in the demo. Secret from `openssl rand -hex 32`. [source: FastAPI oauth2-jwt page]
- **What the FastAPI tutorial is**: `OAuth2PasswordBearer(tokenUrl="token")` + form login (needs `python-multipart`, included in `fastapi[standard]`) + bearer JWT. It says nothing about cookies or sessions. [source: https://fastapi.tiangolo.com/tutorial/security/first-steps/]
- **Where it is dated**: OAuth 2.1 (draft-ietf-oauth-v2-1-17, updated 2026-10-30, still an Internet-Draft) requires PKCE and does not specify the implicit or password grants. [source: https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/] Teach the tutorial as "our own login endpoint that issues a token", and "Login with GitHub/Google" as authorization-code + PKCE / OpenID Connect through a library (Authlib 1.9.9) or a provider; never hand-rolled. [memory] for the library recommendation.
- **Cookies vs tokens in the browser**: OWASP: session IDs >=64 bits entropy from a CSPRNG; cookies `Secure`, `HttpOnly`, `SameSite=Strict` (or Lax), `__Host-` prefix; regenerate the session ID at login; idle + absolute timeouts enforced server-side; do not store tokens in `localStorage`/`sessionStorage`; alternatives are HttpOnly cookies or a Backend-for-Frontend. [source: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html] With `app.frontend()` the React build and the API share one origin, so cookie auth needs no CORS in production. Suggested teaching order: hashing -> session cookie login -> JWT bearer for non-browser clients -> OAuth2/OIDC awareness.
- 401 = not authenticated (send `WWW-Authenticate`), 403 = authenticated but not allowed.

## 9. REST API design norms (handbook-ready, with sources)

| Topic | Norm to teach | Basis |
|---|---|---|
| Resources | plural nouns, no verbs in URLs, kebab-case path segments, no trailing slash, snake_case JSON fields and query params | [source: https://opensource.zalando.com/restful-api-guidelines/ rules 134, 141, 129, 136, 118, 130] |
| Methods | safe = "essentially read-only": GET, HEAD, OPTIONS, TRACE. "PUT, DELETE, and safe request methods are idempotent." POST and PATCH are not | [source: https://www.rfc-editor.org/rfc/rfc9110.html 9.2.1, 9.2.2] |
| Create | POST -> 201 "containing a Location header field"; PUT that creates -> 201, PUT that replaces -> 200 or 204; DELETE -> 204 by convention [memory] | [source: RFC 9110 9.3.3, 9.3.4] |
| Status codes | 200, 201, 204; 400 malformed, 401 unauthenticated, 403 forbidden, 404, 405, 409 conflict with current state, 422 well-formed but invalid, 429 rate limit; 500, 502, 503. Chinese one-liners exist on MDN zh-CN | [source: https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Reference/Status] |
| Errors | RFC 9457 (July 2023, obsoletes RFC 7807), `application/problem+json`; members `type` (default `about:blank`), `title`, `status`, `detail`, `instance`, all optional; extension members allowed (the RFC's own validation example uses an `errors` array with `detail` + `pointer`); "not a debugging tool": no stack traces | [source: https://www.rfc-editor.org/rfc/rfc9457.html] |
| Pagination | design it in from the start: "Adding pagination to an existing RPC is a backwards-incompatible change"; cap the page size. Zalando: "SHOULD prefer cursor-based pagination, avoid offset-based pagination" | [source: https://google.aip.dev/158, Zalando rule 160] |
| Versioning | contested. Google: major version as the first URL segment (`/v1`), never minor versions. Zalando: "SHOULD avoid versioning", "MUST not use URL versioning". GitHub: date-based header `X-GitHub-Api-Version: 2026-03-10`, old versions kept 24 months. All agree additive changes are non-breaking; removing/renaming fields, new required params, type changes are breaking | [source: https://google.aip.dev/185, Zalando rules 113-115, https://docs.github.com/en/rest/about-the-rest-api/api-versions] |
| Idempotency | `Idempotency-Key` header for POST/PATCH is still an IETF draft (draft-ietf-httpapi-idempotency-key-header-08, 2026-10-22): same key + different payload -> 422, still in flight -> 409. Stripe: client-generated key (V4 UUID suggested), saved result replayed "including 500 errors", keys pruned after 24h | [source: https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/, https://docs.stripe.com/api/idempotent_requests] |
| Time, money | RFC 3339 UTC timestamps, names ending `_at`; money as an object with decimal amount + ISO 4217 currency, never a float | [source: Zalando rules 169, 235, 173] |
| Compatibility | "MUST not break backward compatibility"; always return a JSON object at the top level (so fields can be added) | [source: Zalando rules 106, 110] |

Course default (recommendation): `/api/v1` prefix (simplest; maps to `include_router(prefix=...)`), `limit`/`offset` with `le=100` and an envelope `{items, total, limit, offset}` first, cursor pagination as a later refinement, a UNIQUE constraint + 409 as the first idempotency backstop.

Pagination evidence [local] (500,000 rows, `$S/sql/08_pagination.sql`): `LIMIT 5 OFFSET 400000` took 2.08 ms; `WHERE id > 400000 ORDER BY id LIMIT 5` took 0.011 ms with plan `SEARCH posts USING INTEGER PRIMARY KEY (rowid>?)`.

## 10. Layering for small applications

| Layer | Knows about | Must not contain | In the example |
|---|---|---|---|
| Router | HTTP: paths, status codes, headers, `Depends` | SQL, business rules | `routers/notes.py` |
| Schemas (Pydantic) | shape + validation of data crossing the boundary | DB access | `schemas.py` |
| Service | business rules, transaction (`commit`), domain exceptions | `Request`, `HTTPException`, status codes | `service.py` |
| Repository | SQLAlchemy queries | HTTP, business decisions | `repository.py` |
| Models (ORM) | tables, constraints | Pydantic, HTTP | `models.py` |

Domain exceptions (`NoteNotFoundError`) are translated to HTTP in one place (`errors.py`). Honest caveat for lessons: for a 5-endpoint app, router + one `crud.py` is enough; introduce the service layer when the first real business rule appears (here: unique title -> 409) and say why. The official docs do not prescribe these layers.

## 11. SQL teaching sequence (every query run in sqlite3 3.54.0)

Dataset: a tiny bookshop (`authors`, `books`, `customers`, `orders`, `order_items`; Chinese sample data). Files in `$S/sql/`; `01_schema_and_data.sql` builds `shop.db`, and all scripts were re-run end to end from an empty file (database ends in its initial state, `PRAGMA integrity_check` = ok).

Recommended order (the task's nine steps plus the two missing units, marked +):

| # | Unit | Verified demo (file) | Real result to show |
|---|---|---|---|
| 1 | SELECT columns; the CLI (`.mode box`, `.tables`, `.schema`, `.nullvalue NULL`, `.timer on`) | Q1 (02) | 8 rows, rounded box output aligned with CJK text |
| 2 | WHERE, ORDER BY, LIMIT, LIKE/IN/BETWEEN, DISTINCT | Q2-Q4, Q6 (02) | `ORDER BY price DESC LIMIT 3` -> 海边的卡夫卡 52, 挪威的森林 45, 1984 39.9 |
| 3+ | NULL | Q5 (02) | `WHERE city = NULL` counts 0; `IS NULL` finds 小丽 |
| 4 | JOIN (INNER, LEFT), many-to-many through `order_items` | Q7, Q8, Q11 (02) | LEFT JOIN shows 无名氏 with `book_count` 0 |
| 5 | Aggregation: COUNT/SUM/AVG, GROUP BY, HAVING; then subquery, CTE; window functions as awareness | Q9-Q14 (02) | spent per customer: 小红 194.9, 小明 152.8 (cancelled order excluded) |
| 6+ | Writing: INSERT, UPDATE, DELETE, RETURNING, upsert | D4 (09) | `ON CONFLICT (email) DO UPDATE ... RETURNING` works |
| 7 | Modelling and normalisation | M1-M3 (03) | spreadsheet-style table: one UPDATE leaves 小明 with two different emails |
| 8 | Constraints: NOT NULL, UNIQUE, CHECK, FOREIGN KEY, STRICT | C1-C6 (04) | `UNIQUE constraint failed: customers.email`; FK ignored until the PRAGMA |
| 9 | Indexes | I1-I6 (05), 200,000 rows | plan `SCAN events` -> `SEARCH events USING COVERING INDEX ix_events_user_id (user_id=?)`; 3.86 ms -> 0.036 ms; composite index unusable for the second column alone |
| 10 | Transactions | T1-T3 (06) | ROLLBACK restores sum 150; CHECK blocks the overdraft |
| 11 | Migrations | G1-G3 (07) | `ALTER TABLE ... ADD COLUMN level TEXT NOT NULL` -> `Cannot add a NOT NULL column with default value NULL`; then Alembic (5.3) |
| 12 | Python + SQL | `injection_demo.py` | f-string query with `nobody' OR '1'='1` returns every user; the `?` parameter returns none |

```sql
-- three-table JOIN + aggregation (Q11)
SELECT c.name, count(DISTINCT o.id) AS orders, sum(oi.quantity * oi.unit_price) AS spent
FROM customers AS c
JOIN orders AS o       ON o.customer_id = c.id
JOIN order_items AS oi ON oi.order_id = o.id
WHERE o.status <> 'cancelled'
GROUP BY c.id
ORDER BY spent DESC;
```

```text
╭──────┬────────┬───────╮
│ name │ orders │ spent │
╞══════╪════════╪═══════╡
│ 小红 │      2 │ 194.9 │
│ 小明 │      2 │ 152.8 │
╰──────┴────────┴───────╯
```

Notes for lesson writers: the index demo uses `random()`, so row counts differ per run (do not auto-check the count; check that the plan contains `USING` and `INDEX`). In non-interactive use the CLI default mode is `list` (`1||2.5`); always pass `-box` or `.mode box`. CS50 SQL uses nearly the same order (Querying, Relating, Designing, Writing, Viewing, Optimizing, Scaling) and the same SQLite-first approach. [source: https://cs50.harvard.edu/sql/]

SQLite habits that will break on PostgreSQL (teach as a checklist at the switch): double-quoted strings, missing FK enforcement, loose types and booleans as 0/1, bare columns in GROUP BY, case-insensitive LIKE, date functions (`strftime`), transactions continuing after an error (PostgreSQL aborts the transaction [memory]), `.tables`/`.schema` vs psql `\dt`/`\d` [memory].

## 12. Free resources (Chinese availability checked today)

| Resource | Language | Notes | Basis |
|---|---|---|---|
| SQLBolt https://sqlbolt.com | EN | interactive in browser; lessons 1-18: SELECT, constraints, sorting, JOINs, NULLs, expressions, aggregates, execution order, INSERT/UPDATE/DELETE, CREATE/ALTER/DROP | [source] |
| 自学SQL网 http://xuesql.cn | 中文 | Chinese SQLBolt-style lessons 0-12 with in-browser exercises; later lessons are "VIP"; **HTTPS certificate expired** (works over http) | [local curl] |
| 廖雪峰 SQL教程 https://liaoxuefeng.com/books/sql/ | 中文 | MySQL-oriented; 关系模型 (主键/外键/索引), 查询, 修改, 事务 with isolation levels; runs SQL in the browser (AlaSQL) | [source] |
| SQLZoo https://sqlzoo.net/wiki/SQL_Tutorial/zh | 中文 page exists | SELECT -> JOIN -> NULL -> window functions -> self join; translation quality not checked | [source + local curl] |
| CS50 SQL https://cs50.harvard.edu/sql/ | EN (Chinese subtitles not confirmed) | free; SQLite first, then PostgreSQL/MySQL; 7 weeks | [source] |
| Select Star SQL https://selectstarsql.com | EN + 6 other languages, no Chinese | free, no registration; one real dataset | [source] |
| PostgreSQL manual, tutorial part | EN https://www.postgresql.org/docs/current/tutorial.html ; 中文 http://www.postgres.cn/docs/current/ ("PostgreSQL 18.3 手册", http only) | joins, aggregates, views, foreign keys, transactions, window functions | [source + local curl] |
| SQLAlchemy Unified Tutorial https://docs.sqlalchemy.org/en/21/tutorial/ | EN | version 2.1 | [source] |
| FastAPI docs https://fastapi.tiangolo.com/zh/ | 中文 (AI-generated, human-guided) | includes SQL 数据库 page | [source] |
| MDN HTTP status and CORS (zh-CN) | 中文 | https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Reference/Status | [source] |
| 菜鸟教程 SQL / SQLite | 中文 | reachable; reference style, quality variable [memory] | [local curl] |
| pgexercises.com, mystery.knightlab.com (SQL Murder Mystery) | EN | reachable; good practice sets [memory] | [local curl] |

## 13. Alternatives the learner should know exist

| Tool | Version | Fits when | Basis |
|---|---|---|---|
| Django | 6.1.3 (6.1 on 2026-08-05; 6.0 on 2025-12-03) | you want ORM + migrations + admin + auth + templates in one box (content sites, back-office). 6.0 added CSP, template partials, a Tasks API; 6.1 moves to calendar versioning next (Django 2028). APIs via DRF or django-ninja | versions [source: docs.djangoproject.com 6.0/6.1 release notes]; positioning [memory] |
| Flask | 3.1.3 (2026-02-19) | tiny services and a huge body of older tutorials/code; you assemble validation, ORM, docs yourself | version [source]; positioning [memory] |
| Express | 5.3.0 | minimal Node server; State of JS 2025: "still the leader in terms of usage" | [source: https://2025.stateofjs.com/en-US/libraries/back-end-frameworks/] |
| NestJS | 12.5.1 | large TypeScript teams wanting structure (modules, dependency injection, decorators); usage growing | version + trend [source]; positioning [memory] |
| Hono | 4.13.19 | small Web-standard framework for edge/serverless runtimes and Bun/Deno/Node; top-3 satisfaction in State of JS 2025 | [source] + [memory] |
| Next.js | 16.4.6 | React meta-framework with its own server side; SO 2026: 20.6% | [source] |

**Python back end + TypeScript front end vs TypeScript everywhere**

- For TypeScript everywhere: one language for a beginner; Node.js 46.4% and Next.js 20.6% usage (SO 2026); TypeScript became the most-used language on GitHub by monthly contributors in August 2025 (about 2.64M vs Python 2.6M); shared types without code generation; the Octoverse report argues typed languages make AI-assisted coding more reliable. [source: https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/]
- For Python + TypeScript: Python 58.0% vs TypeScript 43.8% usage (SO 2026); FastAPI had the largest gain of the frameworks listed above in both 2025 (the survey calls its +5 points "one of the most significant shifts") and 2026 (14.8 -> 18.5 while Express fell 19.9 -> 15.6); "Python remains dominant for AI and data science workloads" (Octoverse); the learner already owns a Python project and Stages 2-3 build Python engineering habits that Stage 5 reuses; the browser forces JS/TS anyway, so a full-stack engineer learns both; OpenAPI 3.1 + a generated TS client closes most of the type gap; an official maintained template implements exactly this combination.
- Verdict: keep the plan. Add one short comparative lesson ("the same two endpoints in Express or Hono") so the learner can read Node back ends.

## 14. Beginner pitfalls (consolidated)

1. Copying old tutorials: `uvicorn main:app --reload`, `on_event`, `.dict()`, `orm_mode`, `declarative_base()`, `session.query`, `passlib`, `python-jose`, `psycopg2`. See section 3.
2. `curl -d '{...}'` without a JSON Content-Type -> 422; use `curl --json`.
3. 422 vs 400 confusion: FastAPI validation errors are 422 with a `loc` path; read `loc` first.
4. Trailing slash -> 307 redirect; POST clients may not follow it.
5. Route order: fixed paths before parameterised ones.
6. Returning ORM objects without a response model leaks columns (password hashes).
7. One class used as both DB table and API schema (SQLModel style) blurs what clients may send; mass-assignment (`is_admin`) is blocked here by `extra="forbid"` + a separate `NoteCreate`.
8. Tests hitting the real `notes.db`: the engine is created at import from settings; always override `get_session` (or set the URL before import).
9. In-memory SQLite without `StaticPool` (default pool is `SingletonThreadPool`, one database per thread) -> 500 with `sqlite3.OperationalError: no such table: notes` [local].
10. Lifespan not running in tests (needs `with TestClient(app)`).
11. SQLite FK enforcement off unless the PRAGMA is set on every connection.
12. `Base.metadata.create_all()` in production instead of migrations; forgetting to import models in `env.py` (autogenerate then sees no tables [memory]); trusting autogenerate blindly; unnamed constraints.
13. Generating migrations on SQLite and applying them to PostgreSQL.
14. Naive datetimes; `datetime.utcnow()` is deprecated on Python 3.14 [local].
15. Money in floats.
16. String-formatted SQL (injection) instead of parameters.
17. `async def` endpoint calling a blocking DB driver blocks the whole server [source: fastapi.tiangolo.com/async/ explains the threadpool for `def`]; N+1 queries.
18. CORS mistaken for security; `allow_origins=["*"]` with credentials.
19. JWT mistaken for encryption; tokens in `localStorage`; secrets committed to Git (`.env` must be in `.gitignore`).
20. `fastapi run` binds 0.0.0.0 (reachable from the network); `fastapi dev` binds 127.0.0.1.
21. `docker run postgres` (= `latest`) silently jumping to a new major; the 18+ volume path change.
22. SQLite files and `.venv` inside iCloud-synced folders.

## 15. Recommendations for the course

**Teach first (Stage 5 opening):** HTTP by hand (curl `--json`, status codes, headers) -> SQL by hand in `sqlite3` (section 11) -> Python `sqlite3` with parameters -> the flat FastAPI quick start (section 4) with `/docs` and a first pytest -> Pydantic models as the boundary -> SQLAlchemy 2 models + session dependency -> Alembic -> restructure into routers/service/repository + settings + problem details (section 5) -> PostgreSQL via `postgres:18` + psycopg, regenerate migrations, run the SQLite-vs-PostgreSQL checklist.

**Postpone:** async endpoints and async DB; WebSockets, SSE, streaming; Redis, queues, caching; OpenTelemetry; OAuth2 scopes; GraphQL; microservices; NoSQL; FastAPI Cloud (`fastapi deploy` opens a browser login and needs an account).

**Sensible defaults:** `uv add "fastapi[standard]"`; `def` endpoints; `Annotated[...]` dependencies; `lifespan`, never `on_event`; `[tool.fastapi] entrypoint`; `postgresql+psycopg://`; naming convention on `MetaData` from the first model; `render_as_batch` for SQLite; `alembic check` in CI; `TestClient` fixtures with dependency overrides; `pytest -W error` once the learner can read warnings; pin the FastAPI minor in real projects; images pinned by major (`postgres:18`).

**Auto-checkers:** import the learner's `app` and drive it with `TestClient` (no ports, no flakiness); for SQL, run the learner's `.sql` against a fresh copy of `shop.db` and compare result sets; for migrations, `alembic upgrade head` on a temp file then `alembic check`.

**Plain-Chinese analogies:**
- API = 餐厅的菜单和点菜窗口；OpenAPI `/docs` = 自动印出来的菜单。
- router / service / repository = 前台接单员 / 按规矩做菜的厨师长 / 仓库管理员；数据库 = 仓库。
- Pydantic 校验 = 门口安检：不合格的东西不让进门（"在边界校验"）。
- 主键 = 身份证号；外键 = 订单上写的客户编号，必须对应一个真实客户；JOIN = 按编号把两张表对上（像 Excel 的 VLOOKUP）。
- 范式化 = 一件事只记在一个地方，改一处就全改了。
- 索引 = 书后的索引或字典的拼音检索：查得快，但每次加内容都要更新索引。
- 事务 = 银行转账，要么两步都成功，要么都不算；ROLLBACK = 读档。
- 迁移 (migration) = 给数据库结构做的"施工单 + 提交记录"，就像 Git 之于代码。
- ORM = 翻译官，把 Python 对象翻译成 SQL。
- 状态码 = 快递状态：2xx 已签收，4xx 你填错了，5xx 快递公司出了问题。
- 幂等 = 电梯按钮，按一次和按十次效果一样；Idempotency-Key = 防止重复下单的订单号。
- offset 分页 = 从第一页数到第四千页；cursor 分页 = 夹书签。
- 密码哈希 = 绞肉机，肉能变肉馅，肉馅变不回肉；salt = 每个人加不同的调料。
- JWT = 盖了章的手环，谁都能看内容，但改了就失效；session cookie = 存包处的号码牌，东西在服务器。
- CORS = 浏览器执行的门卫规则，不是服务器的防火墙。
- SQLite 与 PostgreSQL = 一个文件的记事本 与 有前台、能同时接待很多人的银行金库。
- 环境变量配置 = 同一份菜谱，在不同厨房用不同火力。

## 16. Where the evidence challenges the plan

1. Stage 5 needs PostgreSQL but Docker is Stage 8. Either add a "Docker as an appliance" mini-lesson in Stage 5 (`docker compose up` for `postgres:18`), or use Postgres.app/Homebrew there. SQLite-only until Stage 8 is not recommended (types, timezones, transaction behaviour differ).
2. Stage 5's list omits ORM, migrations and API-design norms explicitly; add SQLAlchemy, Alembic, problem details, pagination, layering as named outcomes.
3. The SQL sequence should include writing data and NULL; consider moving units 1-5 of section 11 forward (right after Python fundamentals): they need no web knowledge, SQL is the #2 language in SO 2026, and they give quick wins.
4. Do not follow the FastAPI docs verbatim for (a) SQL (SQLModel 0.0.x, `on_event` in the sample), (b) tests (`uv add httpx`), (c) auth storage (the tutorial ends at bearer tokens; add cookie sessions and the OWASP storage guidance in Stage 7).
5. "Auth" in Stage 7 should be ordered hashing -> sessions -> JWT -> OAuth2/OIDC, with OAuth 2.1 named as the direction.
6. Because FastAPI 0.x minors break things, the handbook needs a "how to upgrade a dependency" procedure (read release notes, bump, run tests) by Stage 5, not Stage 9.
7. If the workspace is in an iCloud-synced folder, it should move out before the first database or virtualenv lesson.
8. Serving the built React app with `app.frontend()` gives Stage 7 a same-origin deployment story; CORS then becomes a dev-time topic (Vite dev server origin) rather than a production requirement.

## 17. Not verified

- Anything requiring a listening port or Docker: `fastapi dev` / `fastapi run` actually serving, Swagger UI in a browser, a real PostgreSQL connection through psycopg, applying migrations to PostgreSQL (only the offline SQL was rendered), Redis.
- Whether PostgreSQL 19 went GA today, and psycopg 3.3.x / SQLAlchemy behaviour against 19.
- The sqlite3 interactive default output mode on a real terminal (no pty here; `-interactive` showed `list`).
- Long-term status of `httpx` vs `httpx2` (the encode/httpx repository is not archived; FastAPI docs have not switched wording yet).
- Exact State of JS 2025 percentages (charts not readable); Chinese subtitle availability for CS50 SQL; translation quality of SQLZoo zh and FastAPI zh.
- Positioning statements for Django, Flask, NestJS, Hono beyond versions; CSRF specifics; RFC 5789 PATCH semantics; PostgreSQL rejecting `DEFAULT 0` on boolean and aborting transactions after an error [memory].
- fastapi-users (15.0.5, last release 2026-03-27) maintenance status; PostgreSQL-backed queue libraries.

## 18. Scratch file index

- `$S/notes-api/` verified engineering-layout project (run: `cd $S/notes-api && UV_CACHE_DIR="$TMPDIR/uv-cache" uv run --no-sync pytest -q -W error`).
- `$S/probe/awesome-project/` official quick start; `$S/probe/sqlmodel-probe/` SQLModel check; `$S/probe/fe/dist/` static build for the `app.frontend()` check.
- `$S/sql/01_schema_and_data.sql` ... `09_sqlite_vs_postgres.sql`, `injection_demo.py`, `shop.db`; `$S/web/` raw copies of the FastAPI doc sources consulted.
