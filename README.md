# Oil Price Forecasting Platform

Full-stack web app for visualizing historical oil prices and generating reproducible forecasts.

- **Backend**: FastAPI (Python 3.11), async SQLAlchemy + Alembic, SQLite
- **Frontend**: React 19 + TypeScript, Mantine, Recharts, TanStack Query
- **Data source**: EIA Petroleum Spot Prices API
- **Auth**: cookie-based JWT (access + refresh), bcrypt password hashing
- **Async forecasts**: FastAPI BackgroundTasks + DB-tracked job states (PENDING → PROCESSING → COMPLETED/FAILED/CANCELED)
- **Reproducibility**: every forecast pins to an immutable `DatasetVersion`; predictions never change after the underlying data is revised

---

## Quickstart

### 1. Configure environment

```sh
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set:

- `EIA_API_KEY` — get one free at <https://www.eia.gov/opendata/register.php>. A working dev key is also kept at `./apiKeyEIAGOV` in this repo.
- `SECRET_KEY` — any long random string.

### 2. Start the stack

```sh
docker compose up -d --build
```

Both services come up:

- `frontend` → nginx on `localhost:3000` (serves the React build, proxies `/api/*` to backend)
- `backend` → uvicorn internal-only on port 8000

The containers start **empty** — no schema, no data yet.

### 3. Initialize the database

In a separate terminal:

```sh
bin/db migrate    # apply Alembic migrations
bin/db seed       # seed users + 5-year EIA history (~30s)
```

On **Windows / PowerShell**, use the `.ps1` wrapper instead.

```powershell
bin/db.ps1 migrate
bin/db.ps1 seed
```

Both are idempotent — re-running them is safe.

### 4. Open the app

<http://localhost:3000>

Two users are seeded so you can log in without registering:

| Role | Email | Password |
|---|---|---|
| Admin | `admin@example.com` | `admin12345` |
| Regular | `user@example.com` | `user12345` |

Registering a new account works the same as in production (creates a regular user).

---

## Local dev (no Docker)

### Backend

```sh
python -m venv .venv
.venv/Scripts/Activate.ps1     # Windows; or: source .venv/bin/activate
pip install -r backend/requirements.txt

cd backend
$env:PYTHONIOENCODING="utf-8"   # Windows: prevents the FastAPI CLI emoji crash
bash bin/db migrate
bash bin/db seed
fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

### Frontend

```sh
cd frontend
npm install
npm run dev
```

Vite serves on `http://localhost:3000` and proxies `/api/*` to `http://127.0.0.1:8000`.

### Tests

```sh
cd backend
pytest
```

---

## DB management commands

`bin/db` (POSIX shell) and `bin/db.ps1` (PowerShell, for Windows users) at the **project root** are thin wrappers that forward to `docker compose exec backend bin/db ...` — so the same verbs work in and out of Docker, on any OS.

| Command | Effect |
|---|---|
| `bin/db migrate` | Apply pending migrations (`alembic upgrade head`) |
| `bin/db downgrade [rev]` | Revert one revision (or to a specific one) |
| `bin/db generate` | Autogenerate a migration from model changes |
| `bin/db seed` | Run seeders (idempotent — skips users/datasets that already exist) |
| `bin/db reset` | **Destructive**. Wipes `./data`, then migrate + seed |

---

## Architecture

### Backend layer cake

```
routes/       — receive HTTP, declare Depends(get_..._use_case), call execute(), return
use_cases/    — one file per operation; orchestrates services + ALL Pydantic↔ORM transformation
services/     — thin pass-through to repositories (no business logic, no transformation)
repositories/ — SQLAlchemy calls only; one per table
dependencies/ — FastAPI Depends providers wiring repos→services→use case per request
schemas/      — Pydantic request/response models (input validation + output shape)
utils/        — stateless helpers (auth, tokens, hashing, forecasting, errors, logging, rate limit)
```

A route never wires repositories itself. The route says "I need this use case" via `Depends(get_..._use_case)`; the dependency provider builds the full chain against the request-scoped `AsyncSession` and hands the ready use case to the route.

#### Why this layering

- **Routes stay thin** — easy to spot what each endpoint does without scrolling through DB code.
- **Use cases are testable in isolation** — pass in mock services, no FastAPI required.
- **Services own no state** — the repository they wrap holds the session.
- **Repositories know nothing about HTTP** — reusable from background jobs / schedulers / seeders.

### Async handling

- **Every layer is `async def`** — routes, use cases, services, repositories.
- **SQLAlchemy async session** (`AsyncSession` + `aiosqlite`) — all DB calls are `await`ed.
- **`BackgroundTasks`** — for fire-and-forget work the client shouldn't wait on (forecast workers, oil fetches triggered by admins).
- **`QueueHandler` logging** — log calls are non-blocking (just enqueue + return). A background thread drains the queue into the console and file handlers. Tested at 1000+ concurrent requests; logging never blocks the event loop.
- **Scheduler** — `AsyncIOScheduler` (APScheduler) registers two cron jobs at startup: daily oil fetch (current week) + weekly revision backfill (trailing 6 weeks).

### Authentication flow

- **Register/login** → server issues two JWTs:
  - `access_token` (15 min) — `httpOnly` cookie, sent on every request.
  - `refresh_token` (7 days) — `httpOnly` cookie, used only to mint new access tokens.
- **Passwords** hashed with `bcrypt` (72-byte truncation handled).
- **Get current user** → `app/utils/auth.py:get_current_user` reads the access cookie, decodes the JWT, fetches the user.
- **Auto-refresh** → axios interceptor in `frontend/src/api/client.ts` catches 401, calls `/api/auth/refresh` once, retries the original request. If refresh also fails, the SPA clears the session.
- **Role gate** → `app/utils/auth.py:require_admin` depends on `get_current_user`, then checks the user has the `admin` role. Used on every `/api/admin/*` route.
- **Cookies are set/cleared by the backend** via `Set-Cookie`. Frontend uses `withCredentials: true` so cookies attach automatically.

### Forecast pipeline (reproducibility-first design)

```
POST /api/forecasts                    (1) Validate request, look up latest DatasetVersion
                                       (2) Reject duplicates (same user/model/target/dataset/window)
                                       (3) Create ForecastJob (status=PENDING)  ← committed
                                       (4) BackgroundTasks.add_task(run_forecast, job_id)
                                       (5) Return 202 + job snapshot

Background worker (run_forecast_job)   (a) Re-load job; if CANCELED before pickup, return
                                       (b) PENDING → PROCESSING + started_at  ← committed (polling clients see the flip)
                                       (c) Load history from the pinned DatasetVersion
                                       (d) Dispatch to the right model function
                                       (e) bulk_create forecast points
                                       (f) PROCESSING → COMPLETED + completed_at  ← committed (atomic with points)
                                       Failure path: rollback in-flight points, mark FAILED + error_message, commit in isolation

GET /api/forecasts/{id}                Owner-checked; returns full snapshot incl. points
GET /api/forecasts/latest-matching     For the dashboard auto-overlay (newest COMPLETED for a target)
POST /api/forecasts/{id}/cancel        PENDING-only → CANCELED
DELETE /api/forecasts/{id}             Owner-checked delete
```

#### Reproducibility — the headline requirement

> "Every generated forecast must remain reproducible later even if the underlying dataset changes."

Implemented via three mechanisms:

1. **Pinned dataset version.** At job creation, `ForecastJob.dataset_version_id` is set to `DatasetVersion.get_latest()` and never updated. The worker reads history filtered by that version, not "current" data.
2. **Pinned model + parameters.** `forecast_model` is a versioned enum (`linear_regression_v1`, `holt_winters_v1`). Even if a future model upgrade ships, old jobs still reference their original implementation. `history_weeks` and `horizon_weeks` are stored per-job so the inputs to the model are fully reconstructable.
3. **Immutable points.** `ForecastPoint` rows are append-only. No update logic exists.

When the EIA revises a price (e.g. corrects last week's value), the next scheduled fetch detects a different content hash → creates a **new** `DatasetVersion`. Older versions are never touched. Existing forecasts still point to their original version → their predictions are unchanged.

The UI surfaces this via `ForecastJobResponse.is_based_on_latest_data`: a small "Newer data" badge appears on forecasts whose pinned version isn't the latest, so the user knows they can re-run with newer inputs.

#### Why system-controlled history/horizon

History weeks (104 for linear, 156 for Holt-Winters) and horizon weeks (8 for both) are **system constants** in `app/utils/forecasting/dispatcher.py` — the user doesn't pick them.

- **Holt-Winters needs ≥2 seasonal cycles** (104 weeks) to be stable. Letting users pick less = broken forecasts. We give it 156 (3 cycles) for headroom.
- **Duplicate prevention works cleanly** — two forecasts with the same model+target+dataset are inherently the same.
- **Stored per-job for reproducibility** — even though they're constants today, the *job record* captures the exact values used, so a future change to the constants doesn't retroactively redefine what an old forecast saw.

#### Why two models

- **Linear regression v1** — `numpy.polyfit` degree 1. Cheap, deterministic, robust on any input. Good baseline.
- **Holt-Winters v1** — `statsmodels` triple exponential smoothing with 52-week seasonal period. Captures level + trend + yearly seasonality. Needs more data, more compute, but better for oil-price-like series.

The user picks one, or compares both side-by-side on the "New forecast" page.

#### Duplicate prevention

When a user POSTs an identical forecast (same `user_id` + `forecast_model` + `oil_series_id`/`units` + `dataset_version_id` + `history_weeks` + `horizon_weeks`) and an existing one is in `PENDING`/`PROCESSING`/`COMPLETED` state → 409 `FORECAST_ALREADY_EXISTS`. `FAILED`/`CANCELED` don't block — those are useful retry targets.

The check is one extra query in `CreateForecastJobUseCase` before the insert. Implemented in `ForecastJobRepository.find_existing_duplicate`.

### Logging

**Why a QueueHandler?** Synchronous file I/O blocks the event loop. Under load (1000+ concurrent requests), a 1 ms file write becomes catastrophic when multiplied by every log statement. So:

1. Root logger has **one** handler: a `QueueHandler` that just enqueues the record. Microseconds; never blocks.
2. A `QueueListener` runs in a background thread, draining the queue and dispatching to:
   - **Console handler** → plain text, picked up by `docker logs`.
   - **`DatedRotatingFileHandler`** → `/app/data/logs/app.current.log`, JSON-per-line, rotates by size, renames rotated files to encode their date range (e.g. `app.2026-01-20_to_2026-02-21.log`).
3. The admin `/api/admin/logs` endpoint reads files directly. Date filters use the rotated filename ranges to skip non-overlapping files without opening them.

**Never logged**: passwords, password hashes, tokens of any kind, refresh-token contents, session contents. **Safely logged**: user ids, emails on failure paths (for incident response), public identifiers, status transitions, error categories.

### Rate limiting

`slowapi` with two key functions:

- **Per IP** for anonymous routes (register/login/refresh). Honors `X-Forwarded-For` so the nginx proxy doesn't collapse every client into one bucket.
- **Per user** for authenticated mutations (`POST /forecasts`, `POST /oil/fetch`). Decodes the access cookie inline (no DB hit) for the key.

Defaults are `10/minute`. Each is tunable via env var without touching code. Storage is in-memory (single-process); for a multi-process deploy, Redis can do the job

> **About `request: Request` in rate-limited routes:** `slowapi` looks up the FastAPI `Request` argument **by name**, not by type annotation. Any other name (e.g. `_request`) raises at decoration time. This is the one case where the generic `request` name is mandatory; body schemas in these routes use `<noun>_request` (e.g. `login_request: LoginRequest`) so the two coexist.

### Error handling

Errors live in `app/utils/errors/`, split by kind:

- **HTTP errors** (`http_errors.py`) — `ErrorDefinition` dataclass + `http_error()` factory + every HTTP error as a named constant. Routes raise via `http_error(USER_NOT_FOUND)`, never inline `HTTPException(status_code=..., detail=...)`.
- **Non-HTTP messages** (`messages.py`) — strings stored in DB columns (e.g. `ForecastJob.error_message`) or surfaced through worker logs. They never become HTTP responses, so they carry no status code.

This separation prevents the worst pattern: leaking raw exception strings into the HTTP response or DB. Every user-facing error message is reviewable in one file.

### Multi-user safety

Every forecast read filters by `user_id == current_user.id`. Missing job *or* ownership mismatch → 404 (not 403), so the API doesn't leak which IDs exist. The shared `_owner_check.py` enforces this consistently across `Get`, `Cancel`, and `Delete`.

---

## Database schema

### Tables and relationships

| Table | Purpose | Notable columns | Relationships |
|---|---|---|---|
| `users` | Auth identity | `id`, `email` (unique, indexed), `hashed_password`, `is_active`, `created_at` | has one `profile`, has many `user_roles`, has many `forecast_jobs` |
| `profiles` | 1:1 profile fields | `id`, `user_id` (FK→users unique), `first_name`, `last_name`, `bio` | belongs to `user` |
| `roles` | Role catalog | `id`, `name` (unique) | seeded with `user`, `admin` |
| `user_roles` | M:N user↔role | `(user_id, role_id)` composite PK | both FKs CASCADE on delete |
| `oil_series` | EIA series metadata | `id`, `series` (unique), `duoarea`, `area_name`, `product`, `product_name`, `process`, `process_name`, `units` | has many `oil_price_records`; static (one row per EIA series) |
| `dataset_versions` | Immutable fetch snapshots | `id`, `fetched_at`, `hash` (unique SHA256 of rows), `record_count`, `date_from`, `date_to`, `source` | has many `oil_price_records` |
| `oil_price_records` | Historical prices | `id`, `oil_series_id` (FK), `dataset_version_id` (FK), `period`, `value`. Unique on `(oil_series_id, period, dataset_version_id)` | belongs to both `oil_series` and `dataset_version`. Both FKs CASCADE |
| `forecast_jobs` | Async forecast tracking | `id`, `user_id`, `status`, timing fields, `error_message`, `dataset_version_id` (FK RESTRICT), `forecast_model`, `history_weeks`, `horizon_weeks`, target: `oil_series_id` (FK RESTRICT, nullable) OR `units` | has many `forecast_points` |
| `forecast_points` | Predicted weekly values | `id`, `forecast_job_id` (FK CASCADE), `period`, `value` | belongs to `forecast_job`; one row per predicted week |

### Key design decisions

1. **UUID primary keys everywhere.** Stored as 32-char hex in SQLite (no native UUID type). Reasoning: IDs are publicly exposed (URLs, logs); auto-incrementing integers leak resource counts and enable enumeration attacks. UUIDs are also safe for distributed inserts and future horizontal sharding.

2. **`DatasetVersion` is immutable.** Once a fetch produces a version, neither its `hash` nor its child `oil_price_records` ever change. The next fetch either skips (hash matches → no-op) or creates an entirely new `DatasetVersion` (hash differs → snapshot the new state). This is the foundation for forecast reproducibility — predictions can always point to the exact dataset they used.

3. **`forecast_jobs.dataset_version_id` is `ondelete=RESTRICT`.** A dataset version cannot be deleted while any forecast still references it. Same for `oil_series_id`. This prevents a maintenance operation from silently invalidating historical forecasts.

4. **`forecast_jobs` carries `oil_series_id` XOR `units`** for the target. Single-series mode → `oil_series_id` is set. Aggregate mode → only `units` is set (and the worker averages over all series matching that unit). Validated by the request schema; an exclusive-or design avoids the "both set" ambiguity.

5. **`status` is a CHECK-constrained enum.** Stored as lowercase strings (`pending`/`processing`/...). The DB rejects unknown values; the app code uses a Python `StrEnum`. Two layers of protection.

6. **Unique constraint on `(oil_series_id, period, dataset_version_id)`** in `oil_price_records`. Same week can exist in multiple versions (EIA revised it once); but never twice in the same version. Captures the revision-handling intent at the schema level.

7. **Two-commit forecast worker.** The worker commits twice — once when flipping PENDING → PROCESSING (so the frontend's polling sees the transition), and once when committing the points + COMPLETED status atomically. Without the first commit, the user sees no feedback until the entire computation finishes. Failure path rolls back any in-flight points, then commits FAILED status in a fresh transaction so the error message persists.

### Migrations

Three Alembic migrations:

- `0001_initial` — users, profiles, roles, user_roles. Seeds `user` + `admin` roles.
- `0002_oil_tables` — oil_series, dataset_versions, oil_price_records.
- `0003_forecast_tables` — forecast_jobs, forecast_points + status enum.

Run with `bin/db migrate`. They are not auto-applied at container startup — explicit step, so a misconfigured environment doesn't accidentally `DROP TABLE`.

### Seeders

- `user_seeder` — creates two demo accounts (admin@example.com, user@example.com).
- `oil_seeder` — fetches 5 years of EIA history into the first `DatasetVersion`.

---

## Frontend overview

Built with **Mantine** (component library) + **TanStack Query** (server-state) + **Recharts** (charts) + **React Router 7**.

### Pages

| Path | Page | Notes |
|---|---|---|
| `/` | Login/Register | Centered card, auto-redirects to `/dashboard` when logged in |
| `/dashboard` | Oil price chart with forecast overlay | Target picker (aggregate by unit OR single series), view-period presets (All / 1y / 3m / 3w / This week). Auto-overlays the user's newest COMPLETED forecast matching the current target. "Run forecast" button navigates to `/forecasts/new` with target pre-filled. |
| `/forecasts/new` | Create + visualize | Minimal form (target + model + "Compare both models" checkbox). After submit, chart slot(s) poll every 2s until terminal. Failed slot shows "Try again". Toggling the model dropdown when both charts are visible swaps positions instantly (no extra API calls). |
| `/forecasts` | Management table | Paginated; columns: Created / Model / Target / Status / Data freshness / Actions. Click "Chart" on a completed row to expand inline. Cancel pending. Delete any. |
| `/profile` | View/edit profile | First name, last name, bio. |
| `/admin/users` | Admin user management | Activate/deactivate switch, role badges with remove, "Assign role" modal. |
| `/admin/logs` | Admin log viewer | Paginated; filters by level / logger / search / date range. |

### State + data flow

- **`useSession`** — fires `/api/auth/refresh` on mount; caches the resulting user. Listens for auth-invalidation events from the axios interceptor.
- **`useForecastSlot`** — the brain of the new-forecast page. Per model+target pair, it: auto-fetches latest-matching on mount, polls every 2s while non-terminal, surfaces errors with a retry action, deduplicates by checking for an existing usable forecast before POSTing.
- **All mutations invalidate the relevant query keys** so the list/dashboard update without manual refetches.

---

## Project structure

```
project root/
├── docker-compose.yml          backend + frontend services, single SQLite volume
├── bin/db                      host-side wrapper → docker compose exec backend bin/db ...
├── backend/
│   ├── Dockerfile              python:3.11-slim + uvicorn
│   ├── bin/db                  container-side: alembic + seeders
│   ├── alembic/                migrations (0001 / 0002 / 0003)
│   └── app/
│       ├── main.py             FastAPI app, CORS, lifespan (scheduler), /health
│       ├── config.py           Settings (pydantic-settings) + app-wide constants
│       ├── routes/             auth, profile, admin, oil, forecasts
│       ├── dependencies/       Depends providers (one per use case)
│       ├── use_cases/          one file per operation
│       ├── services/           thin pass-through to repositories
│       ├── repositories/       SQLAlchemy calls only
│       ├── database/           base.py (engine/session), models/, seeders/
│       ├── schemas/            Pydantic request/response models
│       ├── utils/              auth, tokens, password, hashing, dates, errors,
│       │                       forecasting (model dispatcher + linear + Holt-Winters),
│       │                       logging_setup (queue + dated rotating file),
│       │                       rate_limit (slowapi keys + setup)
│       └── scheduler/          APScheduler + cron jobs (daily fetch, weekly revision)
└── frontend/
    ├── Dockerfile              node:20-alpine builder → nginx:alpine
    ├── nginx.conf              proxies /api/* to backend:8000, serves SPA otherwise
    ├── vite.config.ts          dev proxy to 127.0.0.1:8000 + @/* alias
    └── src/
        ├── main.tsx            MantineProvider, QueryClient, Router
        ├── App.tsx             routes + RequireAuth / RequireAdmin guards
        ├── api/                client (axios + refresh interceptor), auth/oil/forecasts/admin/errors
        ├── hooks/              session, login, register, logout, profile, oil, forecasts,
        │                       forecast slot (per-model state machine), admin
        ├── components/         RequireAuth/Admin, AppLayout, forms, OilPriceChart,
        │                       forecasts/ (HistoryAndForecastChart, ForecastChartSlot, badge, target helpers)
        └── routes/             one file per page
```

---

## Known limitations & future work

- **Single-process rate limit storage.** We can swap to Redis or any other similar service.
- **Daily/weekly fetch only covers ~6 weeks back.** Revisions to data older than 6 weeks aren't picked up. A periodic backfill across the full 5-year history would close this gap.
- **No websockets.** Forecast polling uses 2s intervals. Sufficient for jobs that complete in seconds; for slower model classes, websockets are the ones that can be used.
- **Admin role promotion via API not exposed.** The seeded admin is the initial admin; promote others by signing in as admin and using the `/admin/users` page.
- **Frontend has no `dev` script in Docker.** The frontend container is production-style (nginx + built static files); the dev server is host-only.

---

## Tested with

- Python 3.11.x
- Node 20.x
- Docker Desktop / Docker Engine 24+
- Windows 11, Linux

Tests live under `backend/tests/`. Unit tests cover the forecasting functions (determinism, model minimums). Integration tests cover forecast lifecycle (status transitions, cancel/delete, owner isolation) and reproducibility (dataset-version pinning).
