# PharmaBridge Technology Stack & Versions

This document records the exact runtime environments, frameworks, and tooling versions used to implement, test, and run the PharmaBridge workspace.

---

## 1. Operating System & Core Runtimes

| Component | Version | Installation Details / Path |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 Enterprise (win32-x64) | PowerShell 5.1 / pwsh |
| **Python** | 3.12.15 | Managed via `uv` at `C:\Users\moins\.local\bin\uv.exe` |
| **PostgreSQL** | 17.2 | Portable win64 at `C:\Users\moins\.local\pgsql\pgsql\bin\postgres.exe` |
| **Node.js** | 22.14.0 | Node win-x64 |
| **pnpm** | 10.5.2 | Node package manager workspace |

---

## 2. Backend Stack (`apps/api`)

| Package / Tool | Version | Purpose |
| :--- | :--- | :--- |
| **FastAPI** | `^0.115.11` | High-performance asynchronous REST API framework |
| **SQLAlchemy** | `^2.0.38` | Async ORM (`asyncpg`) with `selectinload` and `FOR UPDATE` row locks |
| **Alembic** | `^1.15.1` | PostgreSQL database migrations |
| **Asyncpg** | `^0.30.0` | High-throughput asynchronous PostgreSQL driver |
| **Pydantic** | `^2.10.6` | Type validation, serialization, and OpenAPI schemas |
| **Pydantic-Settings** | `^2.8.1` | Typed environment and configuration loading |
| **Passlib (Argon2-cffi)** | `^1.7.4` | Industry-standard Argon2id password hashing |
| **Pytest** | `^9.1.1` | Asynchronous test framework |
| **Pytest-Asyncio** | `^1.4.0` | Async event loop integration for test execution |
| **Uvicorn** | `^0.34.0` | ASGI production server |

---

## 3. Frontend Stack (`apps/web`)

| Package / Tool | Version | Purpose |
| :--- | :--- | :--- |
| **React** | `^19.0.0` | Core UI library |
| **React DOM** | `^19.0.0` | DOM renderer |
| **TypeScript** | `^5.7.3` | Strict static typing (`strict: true`) |
| **Vite** | `^6.4.5` | Next-generation frontend build tool and dev server |
| **Tailwind CSS** | `^3.4.17` | Utility-first CSS framework with medical design system |
| **TanStack React Query**| `^5.66.11` | Asynchronous state management, polling, and cache invalidation |
| **React Router DOM** | `^7.2.0` | Client-side routing with role-based auth guards |
| **Lucide React** | `^1.16.0` | Healthcare and UI icons |

---

## 4. End-to-End Testing (`tests/e2e`)

| Tool / Browser | Version | Viewports Tested |
| :--- | :--- | :--- |
| **@playwright/test** | `^1.50.1` | Automated headless browser testing |
| **Chromium** | `133.0.6943.16` (rev 1155) | - Desktop Chrome: 1440 × 900<br>- Tablet (Galaxy Tab): 768 × 1024<br>- Mobile (Pixel 7): 390 × 844 |

---

## 5. Network & Port Allocations

- **PostgreSQL**: `127.0.0.1:5432` (`db: pharmabridge`, `user: pharmabridge`)
- **FastAPI Backend**: `http://127.0.0.1:8000` (Docs: `http://127.0.0.1:8000/docs`)
- **Vite Web Workspace**: `http://127.0.0.1:5173`
