# InsightCanvas

InsightCanvas is a warm, human-centered data exploration workspace for CSV files. Upload a dataset, ask what you are curious about in plain English, and get a clear visualization with a short explanation of what the pattern means.

The goal is not to generate charts in bulk. It is to help people ask better questions, understand messy datasets faster, and make first-pass analysis feel less intimidating.

## Features

- React + Tailwind frontend with a warm landing page, protected workspace, auth pages, saved sessions, and shared dashboard view
- FastAPI backend with API routes for CSV upload, dataset profiling, question interpretation, chart recommendation, chart generation, report export, and saved sessions
- Secure CSV handling with file type checks, size limits, sanitized filenames, temporary upload storage, and backend validation
- Dataset-agnostic Pandas profiling for row count, column count, data types, logical types, missing values, unique counts, likely ID columns, multi-value categorical columns, numeric summaries, categorical summaries, date detection, and preview rows
- PII-aware profiling that detects email, phone, and name-like columns, redacts their values from previews/RAG/LLM context, and blocks them from visualization axes
- Natural-language question interpretation with optional OpenAI support, RAG context retrieval, and a deterministic fallback planner
- Smart analysis planning for distributions, comparisons, rankings, grouped aggregations, relationships/correlation, trends, derived bins, multi-value category analysis, and outlier prompts
- Data quality guardrails that detect likely ID columns such as `PassengerId` or `anime_id` and avoid misleading identifier distributions
- Plotly chart generation for line, bar, scatter, histogram, pie, box, and correlation heatmap paths
- Reasoning notes, preprocessing steps, suggested alternatives, and data quality warnings returned with each analysis
- Lightweight local auth using HMAC-signed bearer tokens and SQLite users
- Saved analysis sessions with shareable read-only links
- HTML and MVP PDF report export

## Architecture

```text
frontend/
  src/
    components/
    pages/
    services/
    utils/

backend/
  app/
    main.py
    routes/
    services/
      agent_service.py
      ai_service.py
      chart_service.py
      profile_service.py
      quality_service.py
      rag_service.py
    database.py
    schemas.py
  uploads/
  requirements.txt
  .env.example
```

The frontend calls the FastAPI backend at `http://localhost:8000/api` by default. The backend stores uploaded files in `backend/uploads/` and saved sessions in local SQLite at `backend/app.db`.

## Tech Stack

**Frontend:** React, Tailwind CSS, React Router, Plotly / react-plotly.js

**Backend:** FastAPI, Pandas, SQLite, Pydantic

**AI / Analytics:** Optional OpenAI API integration, deterministic fallback planning, RAG-style dataset context retrieval

## Setup

### Backend

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Optional `.env` values:

```text
SECRET_KEY=replace-with-a-long-random-string
OPENAI_API_KEY=
FRONTEND_ORIGIN=http://localhost:5174
MAX_UPLOAD_BYTES=104857600
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

If your backend runs somewhere else, create `frontend/.env`:

```text
VITE_API_BASE_URL=http://localhost:8000/api
```

## API Endpoints

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/datasets/upload`
- `POST /api/datasets/sample/{name}`
- `POST /api/datasets/profile`
- `POST /api/interpret`
- `POST /api/recommend`
- `POST /api/charts/generate`
- `POST /api/rag/search`
- `GET /api/sessions`
- `POST /api/sessions`
- `GET /api/sessions/{session_id}`
- `DELETE /api/sessions/{session_id}`
- `GET /api/sessions/shared/{share_id}/public`
- `POST /api/reports/export`

## Demo Workflow

1. Start the backend on port `8000`.
2. Start the frontend with `npm run dev`.
3. Sign up with a local demo account.
4. Load a sample dataset or upload a CSV.
5. Ask a question such as `Show survival rate by gender`, `Compare ratings across anime types`, or `What factors seem related to happiness score?`.
6. Generate a chart, review the profile, reasoning notes, warnings, and insight, then save the session.
7. Open Saved Sessions to export an HTML/PDF report or use the share link.

## Example Questions

- `Show the distribution of ratings`
- `Compare survival rate by gender`
- `Which genres have the highest average rating?`
- `What factors seem related to happiness score?`
- `Create bins for a numeric column and compare outcomes across them`
- `Find unusual values in this dataset`

## Privacy And Data Handling

- Uploaded CSV files are stored locally in `backend/uploads/`.
- Local demo users and saved sessions are stored in SQLite at `backend/app.db`.
- `.env`, local uploads, local database files, `node_modules`, and build artifacts are ignored by Git.
- Email, phone, and name-like columns are detected as sensitive, redacted from previews/RAG/LLM context, and blocked from visualization axes.

## Screenshots

Add screenshots here before submitting to Handshake:

- Landing page hero
- Analysis dashboard with generated chart
- Dataset profile panel
- Saved sessions page
- Shared dashboard view

## Future Improvements

- Add production OAuth or hosted auth
- Add background jobs for large CSV uploads
- Add richer LLM-based filtering and transformation plans
- Add a vector database for larger RAG indexes
- Add persistent object storage for uploaded datasets
- Add chart image export with Kaleido or browser-side Plotly download
- Add automated backend and frontend tests
- Add deployment configs for Render/Fly.io/Vercel
