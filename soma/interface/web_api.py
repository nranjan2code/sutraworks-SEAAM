from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import threading
import uvicorn
import queue

logger = get_logger("soma.interface.web_api")

app = FastAPI()
app.mount("/frontend", StaticFiles(directory="frontend/dist"), name="static")

websockets = set()
event_queue = queue.Queue()

def websocket_callback(event: Event):
    event_queue.put(event)

class WebAPIService:
    def __init__(self):
        bus.subscribe('all', websocket_callback)
        self.start_web_server()
        self.start_background_sender()

    def start_web_server(self):
        thread = threading.Thread(target=self.run_server, daemon=True)
        thread.start()

    def run_server(self):
        uvicorn.run(app, host=config.api.host, port=config.api.port)

    def start_background_sender(self):
        thread = threading.Thread(target=self.send_events_to_clients, daemon=True)
        thread.start()

    async def send_events_to_clients(self):
        while True:
            event = event_queue.get()
            for websocket in list(websockets):
                await self.send_event_to_websocket(websocket, event)

    @app.websocket("/api/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        websockets.add(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                # Handle incoming messages if needed
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            websockets.remove(websocket)

    async def send_event_to_websocket(self, websocket: WebSocket, event: Event):
        try:
            await websocket.send_json(event.dict())
        except Exception as e:
            logger.error(f"Failed to send event to websocket: {e}")

    @app.get("/api/status", response_class=HTMLResponse)
    async def status(request: Request):
        return "System is running"

    @app.get("/api/vitals")
    async def vitals():
        return {"status": "healthy"}

    @app.get("/api/organs")
    async def organs():
        return {"organs": []}

    @app.get("/api/goals")
    async def goals():
        return {"goals": []}

    @app.get("/api/timeline")
    async def timeline():
        return {"timeline": []}

    @app.get("/api/failures")
    async def failures():
        return {"failures": []}

# REQUIRED ENTRY POINT (zero required args)
def start():
    service = WebAPIService()