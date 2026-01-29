"""
MedScribe Alliance Protocol - Reference Mock Server

This is a complete mock implementation of the MedScribe Alliance Protocol v0.1
for testing and development purposes.

All endpoints return mock data with TODO comments for production implementation.

Run with:
    uvicorn main:app --reload

Visit documentation at:
    http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import discovery, sessions, audio, templates

# Create FastAPI application
app = FastAPI(
    title="MedScribe Alliance Mock Server",
    version="0.1",
    description="Mock implementation of MedScribe Alliance Protocol for testing and development",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(discovery.router, tags=["discovery"])
app.include_router(sessions.router, prefix="/v1", tags=["sessions"])
app.include_router(audio.router, prefix="/v1", tags=["audio"])
app.include_router(templates.router, prefix="/v1", tags=["templates"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MedScribe Alliance Protocol - Mock Reference Server",
        "version": "0.1",
        "protocol": "medscribealliance",
        "discovery_endpoint": "/.well-known/medscribealliance",
        "documentation": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
