"""
FastAPI entry point for Plan B for my SIP backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import lever_coach, plan_b, eval as eval_router

app = FastAPI(
    title="Plan B for my SIP — API",
    description="Educational SIP adjustment coach. Never investment advice.",
    version="1.0.0",
)

# CORS — allow the Next.js frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(lever_coach.router, prefix="/api")
app.include_router(plan_b.router, prefix="/api")
app.include_router(eval_router.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}

