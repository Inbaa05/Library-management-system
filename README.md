# Library Management Comment Optimization System

A full-stack academic project for **Clean Coding & DevOps (IBM)** — a centralized digital platform where students submit library feedback, and librarians gain actionable insights through automated comment processing, duplicate detection, categorization, and dashboards.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, React Router 6, Recharts, Lucide React |
| Backend | Python 3.11+, Flask 3, SQLAlchemy 2, Flask-Migrate, Flask-CORS |
| Database | SQLite (dev), PostgreSQL (production-ready) |
| Auth | JWT tokens, Werkzeug password hashing |
| Testing | Pytest (backend), Vitest + Testing Library (frontend) |
| CI/CD | GitHub Actions |

---

## Prerequisites

Install these tools before running the application:

1. **Python 3.11+** — https://www.python.org/downloads/
2. **Node.js 18+** with npm — https://nodejs.org/
3. **Git** — https://git-scm.com/

---

## Quick Start

### 1. Clone / Open the Project

```bash
cd library-management-system
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# Copy and edit environment variables
copy .env.example .env

# Initialize database and run migrations
flask db upgrade

# Seed development data (optional, safe to run once)
python seed.py

# Start backend
python run.py
```

Backend runs at: http://localhost:5000

### 3. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Frontend runs at: http://localhost:5173

---

## Creating a Librarian Account (Development)

After seeding, a default librarian account is available:

- **Email**: `librarian@library.edu`
- **Password**: `Librarian@2024`

> ⚠️ Change this password immediately in production. Never expose these credentials publicly.

A student account is also seeded:
- **Email**: `student@library.edu`
- **Password**: `Student@2024`

---

## Environment Variables

### Backend (`backend/.env`)

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///library.db
JWT_SECRET_KEY=your-jwt-secret-change-in-production
CORS_ORIGINS=http://localhost:5173
SIMILARITY_THRESHOLD=0.75
AUTO_APPROVE_LOW_RISK=false
```

### Frontend (`frontend/.env.local`)

```env
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

---

## Running Tests

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### Frontend Production Build

```bash
cd frontend
npm run build
```

---

## Database Migrations

```bash
cd backend

# Apply all migrations
flask db upgrade

# Create a new migration after model changes
flask db migrate -m "describe your change"

# Rollback one migration
flask db downgrade
```

---

## API Documentation

Base URL: `http://localhost:5000/api/v1`

### Health Check
`GET /api/health` → `{"status": "ok", "version": "1.0.0"}`

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register student account |
| POST | `/auth/login` | Login, returns JWT |
| POST | `/auth/logout` | Invalidate token |
| GET | `/auth/me` | Get current user |
| POST | `/auth/change-password` | Change password |

### Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/comments` | Submit feedback |
| GET | `/comments` | List comments (filtered) |
| GET | `/comments/:id` | Get single comment |
| PATCH | `/comments/:id` | Update comment |
| DELETE | `/comments/:id` | Delete (own + librarian) |

### Moderation (Librarian only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/moderation/queue` | Pending review queue |
| POST | `/moderation/:id/approve` | Approve comment |
| POST | `/moderation/:id/flag` | Flag comment |
| POST | `/moderation/:id/archive` | Archive comment |
| POST | `/moderation/:id/restore` | Restore archived |
| GET | `/moderation/:id/history` | Moderation history |

### Books & Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/books` | List books |
| GET | `/books/:id` | Get book detail |
| POST | `/books` | Add book (Librarian) |
| GET | `/books/:id/reviews` | Get reviews |
| POST | `/books/:id/reviews` | Submit review |

### Dashboard (Librarian only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/summary` | Key metrics |
| GET | `/dashboard/trends` | Volume over time |
| GET | `/dashboard/categories` | Category distribution |
| GET | `/dashboard/insights` | Actionable insights |

### Reports (Librarian only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports/comments` | Full report |
| GET | `/reports/export.csv` | Export CSV |

---

## Comment Processing Pipeline

When a comment is submitted, it goes through this automated pipeline:

1. **Normalize** — lowercase, strip whitespace, remove special chars
2. **Validate** — required fields, min/max length
3. **Categorize** — keyword-based category assignment (configurable)
4. **Exact Duplicate Check** — SHA-256 hash of normalized text
5. **Near-Duplicate Check** — Jaccard similarity (configurable threshold: default 0.75)
6. **Relevance Check** — library-domain keyword rules
7. **Appropriateness Check** — configurable blocklist filter
8. **Status Assignment** — Pending/Approved/Duplicate/Irrelevant/Inappropriate
9. **Store** — Save original text + moderation metadata

### Comment Statuses
| Status | Description |
|--------|-------------|
| `pending_review` | Awaiting librarian moderation |
| `approved` | Visible to public |
| `duplicate` | Exact match found |
| `near_duplicate` | High similarity flagged for review |
| `irrelevant` | Off-topic for library context |
| `inappropriate` | Violates content policy |
| `archived` | Removed from active view |

---

## Role-Based Access Control

| Feature | Student | Librarian | Admin |
|---------|---------|-----------|-------|
| Submit feedback | ✅ | ✅ | ✅ |
| View own submissions | ✅ | ✅ | ✅ |
| View approved comments | ✅ | ✅ | ✅ |
| View moderation queue | ❌ | ✅ | ✅ |
| Approve/reject comments | ❌ | ✅ | ✅ |
| View dashboard | ❌ | ✅ | ✅ |
| Export reports | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ✅ |
| View audit logs | ❌ | ✅ | ✅ |

---

## GitHub Actions CI/CD

Workflow triggers on push and pull requests.

See `.github/workflows/ci.yml` for the full pipeline:
- Backend: install deps → run pytest
- Frontend: install deps → run tests → production build

---

## Project Structure

```
library-management-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   ├── migrations/
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   ├── seed.py
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── context/
│   │   └── styles/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
└── README.md
```

---

## Deployment

The application is designed to be deployed on any platform supporting Python and Node.js. Configure:

1. Set production environment variables (never commit secrets)
2. Change `DATABASE_URL` to a PostgreSQL connection string
3. Set `FLASK_ENV=production`
4. Build the frontend: `npm run build`
5. Serve the built frontend through a static host or Flask's static files
6. Use Gunicorn as the WSGI server: `gunicorn run:app`

---

## License

Academic project for IBM Clean Coding & DevOps coursework.
