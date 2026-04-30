# InsightCanvas

InsightCanvas is a warm, human-centered data exploration workspace for tabular files. Upload a dataset, ask what you are curious about in plain English, and get a clear visualization or mini dashboard with short explanations of what the patterns mean.

The goal is not to generate charts in bulk. It is to help people ask better questions, understand messy datasets faster, and make first-pass analysis feel less intimidating.

## Features

- React + Tailwind frontend with a warm landing page, no-login workspace, saved sessions, and shared dashboard view
- FastAPI backend with API routes for dataset upload, profiling, question interpretation, chart recommendation, dashboard analysis, report export, and saved sessions
- Secure CSV, Excel, and JSON handling with file type checks, size limits, sanitized filenames, temporary upload storage, and backend validation
- Dataset-agnostic Pandas profiling for row count, column count, data types, logical types, missing values, unique counts, likely ID columns, multi-value categorical columns, numeric summaries, categorical summaries, date detection, and preview rows
- PII-aware profiling that detects email, phone, and name-like columns, redacts their values from previews/RAG/LLM context, and blocks them from visualization axes
- Natural-language question interpretation with optional LangChain + OpenAI support, RAG context retrieval, and a deterministic fallback planner
- Smart analysis planning for distributions, comparisons, rankings, grouped aggregations, relationships/correlation, trends, derived bins, multi-value category analysis, and outlier prompts
- Quick Insight mode for 1-2 focused charts and Full Dashboard mode for a multi-chart analysis report
- Built-in EDA analyst layer with data quality scoring, duplicate checks, missing-value flags, outlier detection, statistical distribution summaries, correlation scanning, category balance checks, and grouped comparison highlights
- Data quality guardrails that detect likely ID columns such as `PassengerId` or `anime_id` and avoid misleading identifier distributions
- Plotly chart generation for line, bar, scatter, histogram, pie, box, and correlation heatmap paths
- Export tools for downloadable HTML reports, dashboard JSON, browser PDF/print output, and individual chart PNG/JSON files
- Reasoning notes, preprocessing steps, suggested alternatives, and data quality warnings returned with each analysis
- No-login demo flow that opens directly into the dashboard, with saved sessions attached to a local demo user
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
      analysis_service.py
      ai_service.py
      chart_service.py
      data_quality_service.py
      profile_service.py
      quality_service.py
      rag_service.py
      statistics_service.py
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

**AI / Analytics:** Optional LangChain + OpenAI reasoning layer, deterministic fallback planning, RAG-style dataset context retrieval

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
OPENAI_MODEL=gpt-4o-mini
USE_LANGCHAIN=true
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

## Free Deployment

Recommended free hosting:

- **Backend:** Render free web service using `render.yaml`
- **Frontend:** Vercel free React/Vite deployment using `frontend/vercel.json`

Deploy order:

1. Deploy the backend first from this GitHub repo on Render.
   - Blueprint file: `render.yaml`
   - Root directory: `backend`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
2. Add backend env vars in Render:

```text
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini
USE_LANGCHAIN=true
MAX_UPLOAD_BYTES=104857600
FRONTEND_ORIGIN=https://your-vercel-url.vercel.app
```

3. Deploy the frontend on Vercel.
   - Root directory: `frontend`
   - Build command: `npm run build`
   - Output directory: `dist`
4. Add frontend env var in Vercel:

```text
VITE_API_BASE_URL=https://your-render-backend-url.onrender.com/api
```

Render free services may sleep after inactivity, so the first backend request can take a little longer.

## API Endpoints

- `POST /api/datasets/upload`
- `POST /api/datasets/sample/{name}`
- `POST /api/datasets/profile`
- `POST /api/interpret`
- `POST /api/recommend`
- `POST /api/analysis/run`
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
3. Open the dashboard. No signup or login is required.
4. Load a sample dataset or upload a CSV.
5. Choose Quick Insight or Full Dashboard mode.
6. Ask a question such as `Show survival rate by gender`, `Compare ratings across anime types`, or `What factors seem related to happiness score?`.
7. Generate a chart or mini dashboard, review the profile, reasoning notes, warnings, and insight, then save the session.
8. Export the current dashboard as HTML, JSON, browser PDF/print output, or individual chart images.
9. Open Saved Sessions to export an HTML/PDF report or use the share link.

## Example Questions

- `Show the distribution of ratings`
- `Compare survival rate by gender`
- `Which genres have the highest average rating?`
- `What factors seem related to happiness score?`
- `Create bins for a numeric column and compare outcomes across them`
- `Find unusual values in this dataset`

## Analysis Modes

**Quick Insight:** Returns one or two focused visualizations based on the user question and a useful adjacent comparison when the dataset supports it.

**Full Dashboard:** Builds a small analysis report with distributions, category counts, grouped comparisons, correlations, trends, and outlier checks when those views are suitable for the uploaded dataset.

## LangChain Agent Layer

When `OPENAI_API_KEY` is configured and `USE_LANGCHAIN=true`, the backend uses LangChain as the reasoning layer for:

- mapping natural-language questions to structured analysis plans
- choosing suitable columns from the uploaded dataset schema
- selecting chart types and aggregations
- generating dataset-aware suggested questions
- using retrieved dataset context to improve semantic matching

LangChain does not replace Pandas or Plotly. Pandas still performs the actual profiling, cleaning, grouping, aggregation, and statistics, while Plotly generates the visualizations. If LangChain is unavailable or an API call fails, InsightCanvas falls back to the existing deterministic planner and raw OpenAI fallback path.

## EDA Analyst Layer

Each analysis run also returns a lightweight analyst report:

- **Data Quality:** quality score, duplicate rows, high-missing columns, likely identifiers, sensitive fields, constant columns, high-cardinality text fields, and numeric outlier counts
- **Statistical Summary:** numeric mean/median/std/skew, strongest correlations, category imbalance, grouped mean differences, and plain-English takeaways
- **Recommendations:** practical next steps such as cleaning missing values, avoiding ID columns, checking duplicates, and inspecting outliers

This keeps the app from behaving like a single-chart generator. It gives recruiters and non-technical users a clearer sense of whether the dataset is trustworthy and what patterns are worth exploring next.

## Privacy And Data Handling

- Uploaded CSV, Excel, and JSON files are stored locally in `backend/uploads/`.
- The local demo user and saved sessions are stored in SQLite at `backend/app.db`.
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

- Add production OAuth or hosted auth if the app becomes multi-user
- Add background jobs for large CSV uploads
- Add richer LLM-based filtering and transformation plans
- Add a vector database for larger RAG indexes
- Add persistent object storage for uploaded datasets
- Add chart image export with Kaleido or browser-side Plotly download
- Add automated backend and frontend tests
- Add deployment configs for Render/Fly.io/Vercel
