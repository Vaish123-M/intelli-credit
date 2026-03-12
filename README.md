# Intelli-Credit

Intelli-Credit is a full-stack AI-assisted corporate credit underwriting application.

It helps an analyst move from document upload to lending decision through a guided workflow:

1. Upload financial documents.
2. Extract and analyze financial signals.
3. Enrich with external intelligence.
4. Generate risk score and recommendation.
5. Review portfolio-level risk and exposure.
6. Export a CAM-style report.

## Core Capabilities

- Multi-file document upload to FastAPI backend.
- Financial metric extraction from PDF, CSV, and text-like tables.
- Rule-based analysis outputs such as leverage, margins, and risk flags.
- Secondary research engine for external intelligence using News API, SerpAPI, and Google Search API.
- Risk scoring that returns:
	- `risk_score`
	- `risk_category` (`Low Risk` / `Medium Risk` / `High Risk`)
	- `loan_limit`
	- `interest_rate`
	- `decision_status`
- Portfolio and dashboard monitoring:
	- Deal summary
	- Risk distribution
	- High-risk listing
- CAM report text generation and download.
- Copilot Q&A endpoint for contextual credit insights.

## Tech Stack

### Frontend

- React 18 + Vite 5
- Tailwind CSS 4
- Framer Motion
- Recharts
- react-dropzone

### Backend

- FastAPI
- Uvicorn
- pandas
- pdfplumber
- pypdf

## Repository Structure

```text
intelli-credit/
	backend/
		app/
			main.py
		uploads/
		downloads/
	frontend/
		src/
			pages/
			components/
			services/
```

## How the App Works (End-to-End)

1. User uploads files from the Home page.
2. Backend parses file content and extracts financial metrics.
3. Backend builds analysis object and stores it in in-memory app state.
4. User runs research and risk scoring.
5. Risk decision is appended to `state["deals"]` (one latest entry per company).
6. Dashboard and portfolio pages fetch from backend APIs and visualize current state.

## Prerequisites

- Python 3.10+ (tested in this workspace with 3.13)
- Node.js 18+
- npm 9+

## Backend Setup

From repository root (`intelli-credit/`):

```powershell
cd backend
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

Start backend:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Run backend tests:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -q tests
```

Backend docs:

- Swagger UI: `http://127.0.0.1:8000/docs`

## Frontend Setup

From repository root (`intelli-credit/`):

```powershell
cd frontend
npm install
npm run dev
```

Frontend app:

- `http://localhost:5173`

## Hosted Deployment (Judge Access)

Add your public links below before submission so the app is accessible without VPN:

- Frontend URL: `https://intelli-credit-gamma.vercel.app/`
- Backend API URL: `https://intelli-credit-backend-6lnw.onrender.com`
- API Docs URL: `https://intelli-credit-backend-6lnw.onrender.com/docs`

Recommended production split:

- Frontend: Vercel
- Backend: Render (via root `render.yaml`)

## Submission Checklist (Hackathon)

Mark all as complete before submitting:

- [ ] Frontend URL is publicly accessible (no login required for judge demo path).
- [ ] Backend API URL is publicly accessible.
- [ ] API docs URL loads successfully.
- [ ] End-to-end flow works from upload to final report generation.
- [ ] All 5 mandatory document categories are enforced during upload.
- [ ] Dynamic schema editor supports adding/removing fields.
- [ ] Extraction confidence/provenance is visible in API response payload.
- [ ] Test suite runs successfully (`pytest -q tests`).

## Judge Demo Flow (2-3 Minutes)

Use this exact sequence during judging:

1. Open frontend URL and onboard an entity.
2. Upload and classify files for all required document categories:
	- ALM (Asset Liability Management)
	- Shareholding Pattern
	- Borrowing Profile
	- Annual Report
	- Portfolio Cuts / Performance Data
3. Run upload + analysis.
4. Run research and risk score.
5. Generate Final Report and download the PDF.
6. Optionally open `/docs` to show API transparency.

## Deployment Guide (Recommended)

Frontend should be deployed on Vercel. Backend should be deployed on a persistent Python host (for example Render or Railway).

### Frontend (Vercel)

1. Import the repository into Vercel.
2. Set project root directory to `frontend`.
3. Build command: `npm run build`
4. Output directory: `dist`
5. Add environment variable:
	- `VITE_API_BASE_URL=https://intelli-credit-backend-6lnw.onrender.com`
6. Deploy and verify frontend URL loads.

Project includes:

- `frontend/vercel.json`
- `frontend/.env.example`

### Backend (Render)

Render is preconfigured with root-level `render.yaml`.

1. Create a new Blueprint service on Render from this repository.
2. Render auto-detects:
	- root directory: `backend`
	- build command: `pip install -r requirements.txt`
	- start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Set secret env vars in Render dashboard (optional research connectors):
	- `NEWS_API_KEY`
	- `SERPAPI_KEY`
	- `GOOGLE_API_KEY`
	- `GOOGLE_CSE_ID`
4. Set `CORS_ORIGINS` to your frontend URL.
5. Verify API docs at `https://intelli-credit-backend-6lnw.onrender.com/docs`.

Project includes:

- `render.yaml`

### CORS

Backend supports environment-driven CORS via `CORS_ORIGINS`.

- Local dev default: `*`
- Production recommended: set `CORS_ORIGINS` to your exact Vercel domain
	- Example: `https://intelli-credit-gamma.vercel.app/`
  - Multiple origins: comma-separated list

This is already wired in backend startup and ready for hosted deployments.

Deployment readiness checklist:

- Backend CORS allows your frontend domain.
- Frontend `VITE_API_BASE_URL` points to the deployed backend URL.
- Health check endpoint responds on `/`.
- Report downloads work from `/downloads/{filename}`.

## Environment Configuration

Frontend uses `VITE_API_BASE_URL` when present. If not provided, it auto-tries common local backend URLs on port 8000.

Create `frontend/.env` (optional):

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Backend optional API keys for secondary research engine:

```env
NEWS_API_KEY=your_news_api_key
SERPAPI_KEY=your_serpapi_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_custom_search_engine_id
```

If keys are not configured, the backend will use a deterministic fallback dataset so the workflow still functions in local demo mode.

## API Reference

### Upload / Analysis

- `POST /upload`
	- Upload financial files.
	- Returns uploaded file metadata + extracted data + analysis.

- `POST /analyze`
	- Rebuild analysis from extracted data in current state.

- `GET /results`
	- Returns latest uploaded files, extracted data, and analysis.

### Intelligence / Risk / CAM

- `POST /research`
	- Input: `company_name`, optional `promoter_name`.
	- Returns external intelligence signals including:
		- `recent_news`
		- `legal_risk`
		- `sector_outlook`
		- `market_sentiment`
		- `research_features` for downstream risk scoring.

- `POST /risk-score`
	- Input: company name + financial analysis + external intelligence.
	- Returns risk decision object.

- `POST /generate-cam`
	- Input: company, analysis, intelligence, decision.
	- Returns CAM report download URL.

- `GET /downloads/{filename}`
	- Downloads generated CAM report.

### Dashboard / Portfolio

- `GET /dashboard/summary`
- `GET /dashboard/deals`
- `GET /portfolio/summary`
- `GET /portfolio/alerts`
- `GET /portfolio/companies`
- `GET /portfolio/high-risk`

### Copilot

- `POST /copilot/ask`
	- Input: company context + question.
	- Returns generated answer string.

## Frontend Pages (High-Level)

- Home: Upload, analysis, research, scoring, CAM generation.
- Credit Dashboard: Deal-level risk overview and analytics.
- Portfolio Dashboard: Portfolio monitoring with exposure, risk buckets, and high-risk table.

## Data Notes

- Backend persists state to `backend/data/app_state.json`.
- Uploaded files are stored in `backend/uploads` and reports in `backend/downloads`.
- If backend storage is ephemeral on your host, reports/state may reset on redeploy or restart.
- Portfolio demo endpoints (`/portfolio/*`) may include static sample responses depending on endpoint.

## Submission Requirements Coverage

This section maps key challenge requirements to implemented functionality.

1. Enforce 5-document requirement
	- Implemented in backend upload validation and frontend blocker flow.
2. Public deployment links
	- Covered by Hosted Deployment section with frontend/backend/docs URLs.
3. User-defined schema fields
	- Implemented via schema editor (add/remove fields) and backend persistence.
4. Extraction confidence/provenance
	- Included in API extraction results and summarized in responses.
5. Test coverage
	- Backend tests available and runnable via `pytest -q tests`; CI workflow included.

## Troubleshooting

### Frontend shows "Could not connect to backend API"

1. Ensure backend is running on port 8000.
2. Open `http://127.0.0.1:8000/docs` to verify server health.
3. Confirm `VITE_API_BASE_URL` (if set) points to the active backend.

### Port conflict

- Change frontend port: `npm run dev -- --port 5174`
- Change backend port: `--port 8001` and update `VITE_API_BASE_URL`

### CAM file not downloading

1. Verify backend server is still running.
2. Confirm file exists in `backend/downloads`.

## Production Considerations

Before production, add:

- Persistent database for deals/analysis history.
- Auth and role-based access.
- Input validation hardening and rate limits.
- Secure file storage and malware scanning.
- Background job queue for heavy extraction.
- Observability (structured logs, metrics, tracing).

## License

No license file is currently present in this repository.
