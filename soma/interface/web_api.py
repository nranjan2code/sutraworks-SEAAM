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

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse("frontend/dist/index.html")

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

def event_callback(event):
    event_queue.put(event)

def background_sender():
    while True:
        try:
            event = event_queue.get(timeout=1)
            for websocket in list(websockets):
                await websocket.send_json({"type": event.event_type, "data": event.data})
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Background sender error: {e}")

@app.get("/api/status")
async def get_status():
    return {"status": "running"}

@app.get("/api/vitals")
async def get_vitals():
    # Implement logic to fetch vitals data
    return {"vitals": "data"}

@app.get("/api/organs")
async def get_organs():
    # Implement logic to fetch organs data
    return {"organs": "data"}

@app.get("/api/goals")
async def get_goals():
    # Implement logic to fetch goals data
    return {"goals": "data"}

@app.get("/api/timeline")
async def get_timeline():
    # Implement logic to fetch timeline data
    return {"timeline": "data"}

@app.get("/api/failures")
async def get_failures():
    # Implement logic to fetch failures data
    return {"failures": "data"}

def start():
    bus.subscribe('*', event_callback)
    
    sender_thread = threading.Thread(target=background_sender, daemon=True)
    sender_thread.start()
    
    host = getattr(config.api, 'host', '0.0.0.0')
    port = getattr(config.api, 'port', 8000)
    
    def run_server():
        uvicorn.run(app, host=host, port=port)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()