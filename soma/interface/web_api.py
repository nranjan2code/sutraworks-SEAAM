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

# Thread-safe set to store WebSocket connections
websocket_connections = set()

# Queue for background sender thread
event_queue = queue.Queue()

class WebAPIServer:
    def __init__(self):
        # Subscribe to all EventBus events
        bus.subscribe('*', self.on_event)
        
        # Start the background sender thread
        threading.Thread(target=self.background_sender, daemon=True).start()
    
    async def on_event(self, event: Event):
        # Append event to queue for sending to clients
        event_queue.put(event)

    @app.websocket("/api/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        websocket_connections.add(websocket)
        
        try:
            while True:
                data = await websocket.receive_text()
                logger.info(f"Received message from client: {data}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            websocket_connections.remove(websocket)

    @app.get("/api/status", response_class=HTMLResponse)
    async def status(request: Request):
        return HTMLResponse(content="System Status: Online", status_code=200)

    @app.get("/api/vitals")
    async def vitals():
        return {"vitals": "Good"}

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

    def background_sender(self):
        while True:
            try:
                event = event_queue.get()
                for websocket in list(websocket_connections):
                    try:
                        await websocket.send_json({"event_type": event.event_type, "data": event.data})
                    except Exception as e:
                        logger.error(f"Failed to send event to client: {e}")
                        websocket_connections.remove(websocket)
            except Exception as e:
                logger.error(f"Error in background sender: {e}")

# REQUIRED ENTRY POINT (zero required args)
def start():
    organ = WebAPIServer()
    
    def run_server():
        uvicorn.run(app, host=config.api.host, port=config.api.port, workers=config.api.workers)
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()