from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.routers import auth, placement_logs, reflection_notes, attachments, dashboard

# Tables are created directly during the MVP stage; if the schema needs to change later,
# switch to an alembic migration instead of continuing to rely on create_all.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Placement Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(placement_logs.router)
app.include_router(reflection_notes.router)
app.include_router(attachments.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}
