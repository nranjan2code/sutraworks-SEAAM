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

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websockets.add(websocket)
    try:
        while True:
            event = await websocket.receive_text()
            # Handle incoming messages if needed
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        websockets.remove(websocket)

def on_event(event):
    event_queue.put(event)

@app.get("/api/status", response_class=HTMLResponse)
async def get_status():
    return "System is running"

@app.get("/api/vitals")
async def get_vitals():
    # Implement logic to fetch vitals
    return {"vitals": "data"}

@app.get("/api/organs")
async def get_organs():
    # Implement logic to fetch organs
    return {"organs": "data"}

@app.get("/api/goals")
async def get_goals():
    # Implement logic to fetch goals
    return {"goals": "data"}

@app.get("/api/timeline")
async def get_timeline():
    # Implement logic to fetch timeline
    return {"timeline": "data"}

@app.get("/api/failures")
async def get_failures():
    # Implement logic to fetch failures
    return {"failures": "data"}

def background_sender():
    while True:
        try:
            event = event_queue.get()
            for websocket in websockets:
                await websocket.send_text(event.data)
        except Exception as e:
            logger.error(f"Background sender error: {e}")

def start():
    bus.subscribe('*', on_event)
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    sender_thread = threading.Thread(target=background_sender, daemon=True)
    sender_thread.start()

def run_server():
    uvicorn.run(app, host=config.api.host, port=config.api.port)