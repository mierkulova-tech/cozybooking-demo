# CozyBooking — Housing Rental System Backend
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Django](https://img.shields.io/badge/django-5.1-green.svg)

A fully functional backend application (REST API) for housing rentals: listings, search and filtering, user roles, reservations, and reviews. Final project of the Python Advanced course ([It Career Hub](https://itcareerhub.de/at/python-developer)).

**Tech Stack:** Django 5 · Django REST Framework · JWT (SimpleJWT) · PostgreSQL (prod) / SQLite (dev) · Docker.

**Live Deployment:** https://cozybooking-api.onrender.com
**API Documentation (Swagger UI):** https://cozybooking-api.onrender.com/api/docs/
    *_Hosted on Render's free tier — the service spins down after 15 minutes of inactivity, so the first request may take 30–60 seconds (cold start)._*

---

## 1. Architecture

The project is built using a **layered architecture** — each layer has a strict, well-defined responsibility. This is the primary criterion evaluated for "Architecture" and "Code Quality".

```
cozybooking/
├── config/                 # Project settings (settings, main urls, wsgi/asgi)
├── apps/                   # ALL applications bundled in a single package
│   ├── urls.py             # Router collecting URLs from all apps
│   ├── common/             # Shared layer: base model, permissions, errors, helpers, management commands
│   ├── users/              # Users, roles, registration/login/logout (JWT)
│   ├── listings/           # Listings, search/filters/sorting, search/view history
│   ├── reservations/       # Reservations, date overlapping checks, status transitions
│   ├── reviews/            # Reviews and ratings
│   └── tests/              # General integration and model tests
│
├── manage.py
├── requirements.txt
├── .gitattributes
│
├── Dockerfile / docker-compose.yml / entrypoint.sh
└── .env.example
```

Each application follows an identical internal layer structure:

| Folder | Responsibility | Rule |
|---|---|---|
| `choices/` | Enumerations (roles, statuses, housing types) | Enums / constants only |
| `constants/` | Static values (filter keys, page sizes) | Constants only |
| `dto/` | Serializers | Form validation and (de)serialization **only** |
| `errors/` | Domain error classes | Clear error code + HTTP status |
| `filters/` | Search, filtering, sorting | Clean ORM querying |
| `paginations/` | Pagination | Slicing + metadata |
| `models/` | Database models | Table descriptions + full_clean() / CheckConstraint (see section 6) |
| `repositories/` | Database queries | **ONLY** raw queries/fetching, nothing else |
| `services/` | Business logic | "The right way": rules, calculations, permission checks, `@transaction.atomic` |
| `controller/` | Views (route handlers) | Accept request → validate → pass to service |
| `urls.py` | App routes | Own endpoints only |

**Request Flow:**

```
HTTP → controller → (dto: validation) → service (business rules) → repository (DB) → response
```

Why this approach: The controller knows nothing about SQL, the repository knows nothing about HTTP, and business rules reside in a single place making them easy to test. Each layer can be modified independently.

**Project Diagrams**

Class Diagram
![Class Diagram](assets/classes_CozyBooking.png)

Package Diagram
![Package Diagram](assets/packages_CozyBooking.png)

---

## 2. Quick Start (Local, SQLite)

For local development, SQLite is used by default (no PostgreSQL server required).

```bash
# 1. Virtual environment
python -m venv .venv
source .venv/Scripts/activate      # Windows (Git Bash)
# source .venv/bin/activate        # Linux/macOS

# 2. Dependencies
pip install -r requirements-dev.txt

# 3. Environment file
cp .env.example .env               # postgresql=False -> SQLite

# 4. Migrations and startup
python manage.py migrate
python manage.py createsuperuser   # Optional, for /admin
python manage.py fill_db           # Optional: populates DB with demo data (Faker)
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

---

## 3. Running via Docker (PostgreSQL)

The primary database required by the project specifications is PostgreSQL. The entire stack can be launched with a single command:

```bash
cp .env.example .env               
docker compose up --build
```

What happens: The `db` container (`postgres:16-alpine`) starts up with a health check, then the `web` container waits for the database to become available (`entrypoint.sh`), applies migrations, collects static files, and starts via **Gunicorn**.
Docker Compose automatically sets `postgresql=True`, `DB_HOST=db`, and `DB_PORT=5432` for the web container.

### 3.1. Deployment on Render (Production)

The project is deployed on Render — the web service is built directly from the `Dockerfile` (using the same `entrypoint.sh` as in `docker-compose.yml`: migrations and `collectstatic` run automatically on every startup), with a separate managed PostgreSQL database.

Environment variables on Render (Environment -> Web Service):

| Variable | Value |
|---|---|
| `postgresql` | `True` |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | From the Render database Connections block (Internal, not External) |
| `SECRET_KEY` | Generated random string |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |

⚠️ Render Free Tier note: The web service spins down after 15 minutes of inactivity (~30–60 sec cold start on the next request), and the free PostgreSQL database lives for 30 days from creation (+14 day grace period), after which data is deleted — if needed, the database can be re-created (`migrate` + `fill_db` for demo data).

---

## 4. Environment Variables (`.env`)

All secrets must reside exclusively in `.env` (excluded from git via `.gitignore`).

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key (mandatory in production, no default) |
| `DEBUG` | Debug mode (`False` in production) |
| `ALLOWED_HOSTS` | Allowed host names |
| `postgresql` | `True` -> PostgreSQL, `False`/unset -> SQLite (dev) |
| `DB_NAME/USER/PASSWORD/HOST/PORT` | PostgreSQL connection parameters |

---

## 5. API Endpoints

Base prefix: `/api/<version>/`, current version is `v1` (e.g., `/api/v1/listings/`).
Authentication — JWT: header `Authorization: Bearer <access>`.

**How to inspect and test the API (without a frontend — this is a backend project):**
- **Django Admin:** `http://127.0.0.1:8000/admin/` — web panel for data management (requires `createsuperuser`).
- **Postman:** Collection located at `apps/common/management/commands/CozyBooking-demo.postman_collection.json` containing a ready-to-run scenario of 18 requests (logins automatically save tokens and IDs into variables).
- Built-in Swagger/OpenAPI docs are not currently wired up — endpoints can be verified via Postman or Admin.

### Users (`/api/v1/users/`)
| Method | Path | Access | Description |
|---|---|---|---|
| POST | `/register/` | Public | Registration (`name`, `email`, `password`, `role`) |
| POST | `/login/` | Public | Login -> returns `access`, `refresh`, user data |
| POST | `/logout/` | Authenticated | Logout (blacklists `refresh` token) |
| POST | `/token/refresh/` | Public | Refresh `access` token using `refresh` token |
| DELETE | `/me/` | Authenticated | Delete own account |

### Listings (`/api/v1/listings/`)
| Method | Path | Access | Description |
|---|---|---|---|
| GET | `/` | Public | Catalog with filters (see below) |
| POST | `/` | Lessor | Create a listing |
| GET | `/<id>/` | Public | Listing details (records view count) |
| PATCH | `/<id>/` | Owner | Edit listing |
| DELETE | `/<id>/` | Owner | Delete listing |
| POST | `/<id>/availability/` | Owner | Toggle visibility on/off |
| GET | `/my/` | Lessor | My listings (including hidden ones) |
| GET | `/popular-searches/` | Public | Popular search queries |

**Catalog Query Parameters:** `search`, `location`, `price_min`, `price_max`, `rooms_min`, `rooms_max`, `housing_type`, `order` (`price`/`-price`/`created_at`/`-created_at`/`popular`/`-popular`), `page`, `page_size`.

### Reservations (`/api/v1/reservations/`)
| Method | Path | Access | Description |
|---|---|---|---|
| POST | `/` | Renter | Create reservation (`listing`, `start_date`, `end_date`) |
| GET | `/my/` | Authenticated | My reservations (as a renter) |
| GET | `/lessor/` | Lessor | Reservations for my listings (as a lessor) |
| PATCH | `/<id>/confirm/` | Lessor | Confirm reservation (`PENDING -> CONFIRMED`) |
| PATCH | `/<id>/check-in/` | Lessor | Mark as checked-in (`CONFIRMED -> CHECKED_IN`) |
| PATCH | `/<id>/cancel/` | Renter / Lessor | Cancel reservation |

### Reviews (`/api/v1/reviews/`)
| Method | Path | Access | Description |
|---|---|---|---|
| POST | `/` | Renter | Leave a review for a completed reservation |
| GET | `/listing/<id>/` | Public | All reviews for a listing |

---

## 6. Roles and Business Rules

**Roles:** `RENTER` and `LESSOR`. Access control is handled via permission classes `IsRenter` / `IsLessor` (`apps/common/permissions.py`, superuser always passes) and ownership checks inside services.

**Reservation Statuses:** `PENDING -> CONFIRMED -> CHECKED_IN`, or `CANCELED` (from `PENDING` or `CONFIRMED`). Terminal statuses (`CHECKED_IN`, `REJECTED`, `CANCELED`) allow no further transitions.
- Date overlapping: two intervals overlap if `start_A < end_B AND end_A > start_B` (canceled/rejected reservations do not count as occupancy). Checking listing availability is executed under `select_for_update()` to prevent double-booking race conditions.
- Dates cannot be in the past, `start_date < end_date`, and users cannot book their own listings.
- A renter can **cancel** their reservation no later than 2 days before check-in; an ongoing reservation (`CHECKED_IN`) cannot be canceled.
- A lessor can `confirm` (`CONFIRMED`) and `mark check-in` (`CHECKED_IN`, only on actual dates of stay).

**Reviews** can only be left for one's own reservation with the status `CHECKED_IN` and exactly once (enforced by service logic + `OneToOneField` at the database level).

**Data Validation:** Every model (`Apartment`, `Address`, `SearchHistory`, `Reservation`, `Review`, `User`) invokes `full_clean()` before saving — a model cannot be saved bypassing `clean()` or validators, even if an object is created directly via the ORM bypassing the serializer. Additionally, `CheckConstraint` rules are enforced at the database level (price/room/rating ranges, date ordering, etc.) providing dual-layer protection: at the Python level and at the schema level.

---

## 7. Tests
Tests are organized by type within `apps/tests/`:

```
apps/tests/
├── test_full_flow.py                # e2e scenario: registration -> listing -> reservation -> check-in -> review
├── test_models.py                   # full_clean(), CheckConstraint, model boundary values
├── test_services.py                 # service business rules (date overlapping, status transitions, etc.)
├── test_filters_repositories.py     # catalog filtering / sorting / pagination
├── test_edge_cases.py               # additional edge and negative scenarios
└── test_paginations_permissions.py  # pagination and access permissions
```

Execution (isolated test database, `--nomigrations` `--reuse-db` configured in `pytest.ini`):

```bash
python manage.py test
# or, if using pytest:
pytest
```

---

## 8. Security

Security measures implemented in the project:

- **Reservation Integrity:** Explicit state machine for statuses (`ALLOWED_TRANSITIONS`) — you cannot resurrect a canceled reservation or roll back a check-in; reservation creation/modification runs under `@transaction.atomic` and `select_for_update()` on the listing to prevent double-booking race conditions.
- **Two-Tier Validation:** `full_clean()` in model `save()` methods + `CheckConstraint` in the DB (see section 6) — data is protected even when bypassing serializers.
- **Passwords:** Validated through `AUTH_PASSWORD_VALIDATORS` (length, common passwords, digit-only checks), hashed via `set_password` inside `@transaction.atomic` in the user manager.
- **Throttling:** Anonymous and authenticated users are rate-limited by default; auth endpoints (`login`/`register`/`logout`/`refresh`) enforce a strict `5/min` scope against brute-force attacks. _Note: with multiple Gunicorn workers, precise limiting requires a shared cache (Redis) — currently `LocMemCache` tracks per worker._
- **Fail-Closed Configuration:** In production, missing `SECRET_KEY` crashes startup (does not boot with a known default).
- **Production Headers:** Outside `DEBUG`, HTTPS redirect, HSTS, secure cookies, and `SECURE_PROXY_SSL_HEADER` are enabled (behind Gunicorn + proxy).
- **Role-Based & Ownership Access:** Permission classes combined with service-level checks; hidden listings cannot be booked; reviews require a personal `CHECKED_IN` reservation (plus database-level `OneToOne` against duplicates).
- **API Versioning:** All routes go through `URLPathVersioning` (`/api/v1/...`), allowing the introduction of `v2` without breaking existing clients.

---

## 9. Populating the DB with Demo Data
```bash
python manage.py fill_db
```
The command (`apps/common/management/commands/fill_db.py`) uses `Faker` to generate users of both roles, listings with addresses, and a set of reservations — making manual API testing convenient without manual data entry.

## Database Schema (ER Diagram)

The project data structure is illustrated below:

![Database ER Diagram](assets/django_schema.png)
