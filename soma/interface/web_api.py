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

@app.get("/api/status")
async def get_status():
    return {"status": "running"}

@app.get("/api/vitals")
async def get_vitals():
    return {"vitals": "healthy"}

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

def background_sender():
    while True:
        try:
            event = event_queue.get()
            for websocket in websockets:
                await websocket.send_text(event.data)
        except Exception as e:
            logger.error(f"Background sender error: {e}")

def start():
    bus.subscribe('*', event_callback)
    
    def run_server():
        uvicorn.run(app, host=config.api.host, port=config.api.port, workers=config.api.workers)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    sender_thread = threading.Thread(target=background_sender, daemon=True)
    sender_thread.start()