# app_ready.py
import logging
import os
from fastapi import FastAPI
from datetime import datetime

LOG_FILE = "agent_s_startup.log"
READY_FILE = "agent_s.ready"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("agent_s")

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    return {"status": "ready" if os.path.exists(READY_FILE) else "starting"}

def mark_ready():
    with open(READY_FILE, "w", encoding="utf-8") as f:
        f.write(datetime.utcnow().isoformat())
    logger.info("AGENT-S READY FILE CREATED: %s", READY_FILE)

def startup_tasks():
    missing = []
    if not (os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_BASE")):
        missing.append("OPENAI_API_KEY/OPENAI_API_BASE")
    if missing:
        logger.error("Startup checks failed, missing: %s", missing)
        raise SystemExit(1)
    logger.info("Startup checks passed")
    mark_ready()
    logger.info("=== AGENT-S STARTED SUCCESSFULLY ===")

@app.on_event("startup")
async def on_startup():
    try:
        startup_tasks()
    except Exception:
        logger.exception("Startup failed")
        raise
