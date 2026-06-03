import asyncio
import json
import threading
import websockets
from config import WS_PORT


class WebSocketServer:
    def __init__(self):
        self._clients: set = set()
        self._loop: asyncio.AbstractEventLoop | None = None

    async def _handler(self, websocket):
        self._clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self._clients.discard(websocket)

    async def _serve(self):
        async with websockets.serve(self._handler, "localhost", WS_PORT):
            print(f"[WebSocketServer] Listening on ws://localhost:{WS_PORT}")
            await asyncio.Future()  # run forever

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._serve())

    def start(self):
        thread = threading.Thread(target=self._run_loop, daemon=True)
        thread.start()

    def broadcast(self, data: dict):
        if not self._loop or not self._clients:
            return
        payload = json.dumps(data)

        async def _send_all():
            dead = set()
            for ws in list(self._clients):
                try:
                    await ws.send(payload)
                except Exception:
                    dead.add(ws)
            self._clients -= dead

        asyncio.run_coroutine_threadsafe(_send_all(), self._loop)
