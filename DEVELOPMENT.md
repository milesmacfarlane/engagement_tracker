# Development Setup Guide

## Overview

This project is being migrated from Streamlit to a modern Next.js + FastAPI stack.

- **Frontend:** Next.js 14 with TypeScript, Tailwind CSS, React Hook Form
- **Backend:** FastAPI with async SQLAlchemy and PostgreSQL
- **Database:** PostgreSQL (use Neon for production, local Docker for development)

## Project Structure

```
engagement_tracker/
├── frontend/              # Next.js application
│   ├── app/              # Next.js app directory (routes & layouts)
│   ├── components/       # Reusable React components
│   ├── lib/              # Utilities, API client, types
│   └── public/           # Static assets
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # Business logic (to reuse from utils.py)
│   │   ├── database.py   # Database configuration
│   │   └── main.py       # FastAPI app entry point
│   ├── requirements.txt  # Python dependencies
│   ├── Dockerfile        # Docker image definition
│   └── docker-compose.yml # Local PostgreSQL setup
└── .github/workflows/    # CI/CD pipelines
```

## Prerequisites

- **Node.js 18+** (for frontend)
- **Python 3.11+** (for backend)
- **Docker & Docker Compose** (for PostgreSQL)

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Start PostgreSQL (requires Docker)
docker-compose up -d

# Run FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Server:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Start development server
npm run dev
```

The frontend will be available at:
- **Application:** http://localhost:3000

### 3. Database Setup

PostgreSQL runs in Docker for local development:

```bash
# Start PostgreSQL (from backend directory)
cd backend
docker-compose up -d

# View logs
docker-compose logs -f postgres

# Stop PostgreSQL
docker-compose down

# Reset database (clears all data)
docker-compose down -v
```

**Connection Details:**
- **Host:** localhost
- **Port:** 5432
- **User:** postgres
- **Password:** postgres
- **Database:** engagement_tracker

## Development Workflow

### Running Both Services

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - PostgreSQL (if needed):**
```bash
cd backend
docker-compose logs -f postgres
```

## API Development

The backend has skeleton endpoints in `/app/routes/` that are marked with `# TODO: Implement`:

- **Authentication:** `app/routes/auth.py`
- **Students:** `app/routes/students.py`
- **Classes:** `app/routes/classes.py`
- **Observations:** `app/routes/observations.py`
- **Analytics:** `app/routes/analytics.py`
- **Reports:** `app/routes/reports.py`

To implement an endpoint:

1. Add SQLAlchemy queries in the route handler
2. Add request/response Pydantic models if needed
3. Test with `http://localhost:8000/docs`

## Frontend Development

Key directories:

- **`app/`** - Page routes (create `app/dashboard/page.tsx` for `/dashboard` route)
- **`components/`** - Reusable components
- **`lib/`** - API client, types, utilities

Example API call:

```typescript
// lib/api-client.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

export const getStudents = () => api.get('/students');
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests (coming in Phase 2)
```bash
cd frontend
npm run test
```

## Environment Variables

### Backend (`.env`)
See `backend/.env.example`

### Frontend (`.env.local`)
See `frontend/.env.example`

## Building for Production

### Backend
```bash
cd backend
docker build -t engagement-tracker-backend .
```

### Frontend
```bash
cd frontend
npm run build
npm start
```

## Deployment

See `DEPLOYMENT.md` for production deployment instructions.

## Troubleshooting

### PostgreSQL Connection Error
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# View logs
docker-compose logs postgres

# Restart
docker-compose restart postgres
```

### Frontend can't connect to backend
- Ensure backend is running on `http://localhost:8000`
- Check `frontend/.env.local` has correct `NEXT_PUBLIC_API_URL`
- Check CORS settings in `backend/app/main.py`

### Python import errors
```bash
# Reinstall dependencies
cd backend
pip install -r requirements.txt --force-reinstall
```

### Node modules issues
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Contributing

1. Create a feature branch
2. Make changes
3. Run tests and linting
4. Submit pull request

See the implementation plan in the repository for architectural decisions.
