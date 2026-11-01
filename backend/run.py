"""
ScamRadar India — Backend Entry Point
Run with: python run.py
Dynamically evaluates $PORT for cloud deployment (Render, Railway, Heroku, Fly.io, Docker)
"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    is_dev = os.environ.get("ENVIRONMENT", "development").lower() == "development"
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=is_dev,
        server_header=False,   # Suppress "server: uvicorn" fingerprinting header
        date_header=False,     # Suppress "date" header (reduces info leakage)
    )
