"""
Asterix AI — FastAPI Backend Entry Point
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.routers import auth, chat, ai_router, voice, pdf, image, settings


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Initialize resources on startup and clean up on shutdown."""
    await init_db()
    yield


app = FastAPI(
    title="AstraMind AI API",
    description="Backend API for the AstraMind AI mobile assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(ai_router.router, prefix="/api/ai", tags=["AI Router"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(pdf.router, prefix="/api/pdf", tags=["PDF"])
app.include_router(image.router, prefix="/api/image", tags=["Image"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])


@app.get("/api/healthz", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "astramind-ai"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
    