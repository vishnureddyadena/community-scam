"""
ScamRadar Backend — Root Entry Point
Allows cloud platforms (Render, Railway, Heroku, Fly.io) deploying from the repository root
to discover and start the FastAPI service with dynamic port binding.
"""
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    is_dev = os.environ.get("ENVIRONMENT", "production").lower() == "development"
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=is_dev)
