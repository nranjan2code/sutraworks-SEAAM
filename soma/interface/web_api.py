from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import threading
import uvicorn
import queue
import asyncio
import time

logger = get_logger("soma.interface.web_api")

app = FastAPI(title="SEAA API", version="1.0.0")

# Global WebSocket management
websockets = set()
event_queue = queue.Queue()

def websocket_callback(event: Event):
    """Callback for events from the event bus."""
    event_queue.put(event)

# =========================================
# ROOT ENDPOINTS
# =========================================

@app.get("/")
async def root():
    """Root API info endpoint."""
    return {
        "name": "SEAA",
        "version": "1.0.0",
        "description": "Self-Evolving Autonomous Agent API",
        "endpoints": {
            "api": "/api",
            "frontend": "/frontend",
            "docs": "/docs"
        }
    }

@app.get("/frontend/")
async def frontend_root():
    """Serve frontend HTML with corrected asset paths."""
    try:
        with open("frontend/dist/index.html", "r") as f:
            html = f.read()
            # Fix asset paths to be relative to /frontend/
            html = html.replace('src="/assets/', 'src="/frontend/assets/')
            html = html.replace('href="/assets/', 'href="/frontend/assets/')
            return HTMLResponse(content=html)
    except FileNotFoundError:
        return {"error": "Frontend not found"}

# Mount static frontend files
app.mount("/frontend", StaticFiles(directory="frontend/dist"), name="static")

# =========================================
# API ENDPOINTS
# =========================================

@app.get("/api/status")
async def get_status():
    """Get complete system status."""
    return {
        "identity": {
            "id": "seaa-default",
            "name": "SEAA",
            "shortId": "seaa",
            "genesis": "1.0.0",
            "lineage": "TabulaRasa"
        },
        "vitals": {
            "uptime_seconds": int(time.time()),
            "dna_hash": "unknown",
            "organ_count": 0,
            "healthy_organs": 0,
            "sick_organs": 0,
            "goals_satisfied": 0,
            "total_goals": 0
        },
        "organs": [],
        "goals": []
    }

@app.get("/api/vitals")
async def get_vitals():
    return {"status": "healthy"}

@app.get("/api/organs")
async def get_organs():
    return {"organs": []}

@app.get("/api/goals")
async def get_goals():
    return {"goals": []}

@app.get("/api/timeline")
async def get_timeline():
    return {"timeline": []}

@app.get("/api/failures")
async def get_failures():
    return {"failures": []}

# =========================================
# WEBSOCKET ENDPOINT
# =========================================

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time events."""
    await websocket.accept()
    websockets.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        websockets.discard(websocket)

# =========================================
# WEB API SERVICE
# =========================================

class WebAPIService:
    def __init__(self):
        bus.subscribe('all', websocket_callback)
        self.start_web_server()
        self.start_background_sender()

    def start_web_server(self):
        thread = threading.Thread(target=self.run_server, daemon=True)
        thread.start()

    def run_server(self):
        try:
            logger.info(f"Starting uvicorn server on {config.api.host}:{config.api.port}")
            uvicorn.run(app, host=config.api.host, port=config.api.port, log_level="info")
        except Exception as e:
            logger.error(f"Uvicorn server crashed: {e}", exc_info=True)

    def start_background_sender(self):
        import sys
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        try:
            loop = asyncio.get_running_loop()
            asyncio.ensure_future(self.send_events_to_clients())
        except RuntimeError:
            thread = threading.Thread(target=self._run_async_sender, daemon=True)
            thread.start()

    def _run_async_sender(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.send_events_to_clients())
        finally:
            loop.close()

    async def send_events_to_clients(self):
        try:
            while True:
                event = event_queue.get()
                for websocket in list(websockets):
                    try:
                        await websocket.send_json(event.dict())
                    except Exception as e:
                        logger.error(f"Failed to send event to websocket: {e}")
        except Exception as e:
            logger.error(f"WebSocket sender crashed: {e}", exc_info=True)

# REQUIRED ENTRY POINT (zero required args)
def start():
    try:
        logger.info("WebAPIService.start() called")
        service = WebAPIService()
        logger.info("WebAPIService instantiated successfully")
        # Keep the thread alive
        while True:
            time.sleep(1)
    except Exception as e:
        logger.error(f"WebAPIService failed: {e}", exc_info=True)
        raise
