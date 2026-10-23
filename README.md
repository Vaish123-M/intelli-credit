# Intelli-Credit

**AI-Powered Corporate Credit Underwriting Platform**

Intelli-Credit is a production-grade full-stack application that automates corporate credit underwriting through AI-assisted document analysis, risk scoring, and portfolio monitoring. Built with enterprise-grade architecture including JWT authentication, rate limiting, containerization, and observability.

---

## 🚀 Features

### Core Credit Underwriting
- **Multi-Document Upload**: Support for PDF, CSV, and text files with drag-and-drop interface
- **Financial Extraction**: Automated extraction of key financial metrics (revenue, EBITDA, debt, equity, ratios)
- **Document Classification**: Rule-based classification of 5 required document types (ALM, Shareholding, Borrowing, Annual Report, Portfolio)
- **Secondary Research**: External intelligence integration via News API, SerpAPI, and Google Custom Search
- **Risk Scoring**: Weighted risk algorithm combining financial metrics and external signals
- **Decision Engine**: AI-powered credit recommendations with SWOT analysis
- **Report Generation**: CAM-style credit assessment reports with PDF export

### Advanced Features
- **AI Copilot**: Context-aware Q&A powered by Anthropic Claude/OpenAI GPT
- **Portfolio Analytics**: Real-time risk monitoring, exposure tracking, and alert generation
- **Dynamic Dashboards**: Interactive visualizations with Recharts and auto-refresh

### Production-Grade Infrastructure
- **JWT Authentication**: Role-based access control (Admin, Analyst, Viewer)
- **Rate Limiting**: API throttling with slowapi to prevent abuse
- **Docker Containerization**: Multi-container setup with docker-compose
- **Prometheus Metrics**: Application performance monitoring at `/metrics`
- **Grafana Dashboards**: Pre-configured visualization for metrics
- **Structured Logging**: JSON-formatted logs for production debugging
- **CI/CD Pipeline**: GitHub Actions for automated testing

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React 18      │     │   FastAPI       │     │  PostgreSQL     │
│   Frontend      │────▶│   Backend       │────▶│   Database      │
│   (Nginx)       │     │   (Uvicorn)     │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │     Redis       │
                        │  (Cache/Queue)  │
                        └─────────────────┘
```

### Technology Stack

#### Frontend
- **React 18** - UI library with hooks
- **Vite 5** - Build tool and dev server
- **Tailwind CSS 4** - Utility-first styling
- **Framer Motion** - Animations
- **Recharts** - Data visualization
- **react-dropzone** - File upload component

#### Backend
- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **python-jose** - JWT token handling
- **passlib** - Password hashing with bcrypt
- **slowapi** - Rate limiting
- **prometheus-fastapi-instrumentator** - Metrics collection
- **pandas** - Data processing
- **pdfplumber** - PDF table extraction
- **anthropic/openai** - LLM integration

#### Infrastructure
- **Docker** - Containerization
- **docker-compose** - Multi-container orchestration
- **PostgreSQL 15** - Production database
- **Redis 7** - Caching and message broker
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization
- **GitHub Actions** - CI/CD pipeline

### Persistence
- Application state is persisted through SQLAlchemy in the `application_state` table.
- Local development defaults to SQLite at `backend/data/app_state.db`.
- Docker and production deployments can set `DATABASE_URL` to PostgreSQL.
- Existing `backend/data/app_state.json` files are imported automatically on first startup.

---

## 📁 Repository Structure

```
intelli-credit/
├── backend/
│   ├── app/
│   │   ├── auth/              # JWT authentication & RBAC
│   │   │   ├── __init__.py
│   │   │   ├── models.py      # User models
│   │   │   ├── security.py    # Password hashing
│   │   │   ├── jwt_handler.py # Token management
│   │   │   └── dependencies.py # Auth dependencies
│   │   ├── services/          # Business logic
│   │   │   ├── cam/           # Report generation
│   │   │   ├── ml/            # ML models
│   │   │   ├── research/      # External research
│   │   │   └── audit_store.py # Audit logging
│   │   └── main.py            # FastAPI app & endpoints
│   ├── tests/                 # Test suite
│   ├── uploads/               # File upload directory
│   ├── downloads/             # Generated reports
│   ├── data/                  # Application state
│   ├── Dockerfile             # Backend container
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   └── services/         # API client
│   ├── Dockerfile             # Frontend container
│   ├── nginx.conf             # Nginx configuration
│   └── package.json           # Node dependencies
├── .github/workflows/         # CI/CD pipelines
├── docker-compose.yml         # Multi-container setup
├── prometheus.yml             # Prometheus config
├── .env.example               # Environment variables template
└── README.md                  # This file
```

---

## 🚦 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)

### Docker Deployment (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/Vaish123-M/intelli-credit.git
cd intelli-credit
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🔐 Authentication

The application uses JWT-based authentication with role-based access control.

### User Roles
- **Admin**: Full access to all endpoints
- **Analyst**: Can perform credit analysis and view portfolios
- **Viewer**: Read-only access to dashboards

### API Usage

1. **Register a user**
```bash
POST /auth/register
{
  "email": "analyst@example.com",
  "username": "analyst",
  "password": "securepassword",
  "role": "analyst"
}
```

2. **Login to get token**
```bash
POST /auth/login
Content-Type: application/x-www-form-urlencoded
username=analyst&password=securepassword
```

3. **Use token in requests**
```bash
Authorization: Bearer <your_jwt_token>
```

---

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Core Workflow
- `POST /entity-onboard` - Onboard a company entity
- `POST /classify-documents` - Classify uploaded documents
- `POST /upload` - Upload and extract financial data
- `POST /analyze` - Run financial analysis
- `POST /research` - Run external research
- `POST /risk-score` - Calculate risk score and decision
- `POST /generate-cam` - Generate CAM report
- `POST /generate-final-report` - Generate final PDF report

### AI Features
- `POST /copilot/ask` - Ask context-aware questions

### Portfolio & Dashboard
- `GET /dashboard/summary` - Dashboard summary stats
- `GET /dashboard/deals` - All analyzed deals
- `GET /portfolio/summary` - Portfolio summary
- `GET /portfolio/alerts` - Risk alerts
- `GET /portfolio/companies` - All companies
- `GET /portfolio/high-risk` - High-risk companies

### Monitoring
- `GET /metrics` - Prometheus metrics
- `GET /health` - Health check

---

## 🧪 Testing

Run the test suite:
```bash
cd backend
pytest -q tests
```

Run with coverage:
```bash
pytest --cov=app tests/
```

---

## 📈 Monitoring

### Prometheus Metrics
Access metrics at `http://localhost:8000/metrics`

Key metrics tracked:
- Request latency
- Request count by endpoint
- Error rate
- Active connections

### Grafana Dashboards
1. Access Grafana at `http://localhost:3000`
2. Login with `admin/admin`
3. Add Prometheus data source: `http://prometheus:9090`
4. Import pre-configured dashboards

---

## 🔧 Configuration

Key environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | - |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `ANTHROPIC_API_KEY` | Anthropic API key for Copilot | - |
| `OPENAI_API_KEY` | OpenAI API key (fallback) | - |
| `HIGH_RISK_THRESHOLD` | Risk score threshold for alerts | 0.6 |
| `CORS_ORIGINS` | Allowed CORS origins | * |

---

## 🚀 Deployment

### Production Checklist
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set up production PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Add real API keys for external services
- [ ] Enable HTTPS/TLS
- [ ] Set up proper logging aggregation
- [ ] Configure backup strategy for database
- [ ] Set up monitoring alerts

### Deploy to Render
The project includes `render.yaml` for easy deployment to Render cloud platform.

### Deploy to AWS/GCP/Azure
Use the provided Docker images and docker-compose configuration as a template for cloud deployment.

---

## 📝 License

This project is for educational and demonstration purposes.

---

## 👤 Author

Built as a final year computer engineering project to demonstrate full-stack development, AI integration, and production-grade infrastructure.

---

## 🤝 Contributing

This is a portfolio project. For suggestions or improvements, please open an issue or pull request.

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
	- Live frontend URL: `https://intelli-credit-gamma.vercel.app/`
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
