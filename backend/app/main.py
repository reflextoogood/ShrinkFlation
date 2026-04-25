from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine, Base, SessionLocal
from app.models import db as _models  # noqa: F401 — registers ORM models
from app.routers import leaderboard, reports, calculator, receipt, search, agent

app = FastAPI(title="ShrinkFlation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leaderboard.router)
app.include_router(reports.router)
app.include_router(calculator.router)
app.include_router(receipt.router)
app.include_router(search.router)
app.include_router(agent.router)


@app.on_event("startup")
async def startup_event():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    # Load seed data
    from app.seed.loader import load_seed_data
    db = SessionLocal()
    try:
        load_seed_data(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "service": "shrinkflation-api"}
