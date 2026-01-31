from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import threading
import uvicorn
import queue

logger = get_logger("soma.interface.web_api")

app = FastAPI()
templates = Jinja2Templates(directory="frontend/dist")
app.mount("/static", StaticFiles(directory="frontend/dist/static"), name="static")

# Thread-safe set to store WebSocket connections
websocket_connections = set()

# Queue for background sender thread
event_queue = queue.Queue()

def handle_event(event):
    event_queue.put(event)

class WebAPI:
    def __init__(self):
        bus.subscribe('eventbus.*', handle_event)
        self.start_websocket_sender_thread()
        logger.info("Web API initialized and listening for events.")

    async def websocket_endpoint(self, websocket: WebSocket):
        await websocket.accept()
        websocket_connections.add(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                # Handle incoming messages if needed
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            websocket_connections.remove(websocket)

    @app.get("/", response_class=HTMLResponse)
    async def read_root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/api/status")
    async def get_status():
        # Implement logic to fetch and return system status
        return {"status": "running"}

    @app.get("/api/vitals")
    async def get_vitals():
        # Implement logic to fetch and return system vitals
        return {"vitals": "normal"}

    @app.get("/api/organs")
    async def get_organs():
        # Implement logic to fetch and return list of organs
        return {"organs": []}

    @app.get("/api/goals")
    async def get_goals():
        # Implement logic to fetch and return system goals
        return {"goals": []}

    @app.get("/api/timeline")
    async def get_timeline():
        # Implement logic to fetch and return system timeline
        return {"timeline": []}

    @app.get("/api/failures")
    async def get_failures():
        # Implement logic to fetch and return system failures
        return {"failures": []}

    def start_websocket_sender_thread(self):
        def sender():
            while True:
                event = event_queue.get()
                for websocket in list(websocket_connections):
                    try:
                        await websocket.send_text(event.data)
                    except Exception as e:
                        logger.error(f"Failed to send event to client: {e}")
                        websocket_connections.remove(websocket)
        thread = threading.Thread(target=sender, daemon=True)
        thread.start()

# REQUIRED ENTRY POINT (zero required args)
def start():
    organ = WebAPI()
    def run_server():
        uvicorn.run(app, host=config.api.host, port=config.api.port)
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()