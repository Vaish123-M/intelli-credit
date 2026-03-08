from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.cam import router as cam_router
from app.routes.dashboard import router as dashboard_router
from app.routes.research import router as research_router
from app.routes.risk_score import router as risk_score_router
from app.routes.upload import router as upload_router

app = FastAPI(title="Intelli-Credit API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(research_router)
app.include_router(risk_score_router)
app.include_router(cam_router)
app.include_router(dashboard_router)

DOWNLOADS_DIR = Path(__file__).resolve().parents[1] / "downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/downloads", StaticFiles(directory=str(DOWNLOADS_DIR)), name="downloads")


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "Intelli-Credit API"}
