import asyncio
import json
import threading
import websockets
from config import WS_PORT


class WebSocketServer:
    def __init__(self):
        self._clients: set = set()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._last_data: dict | None = None

    async def _handler(self, websocket):
        self._clients.add(websocket)
        if self._last_data:
            try:
                await websocket.send(json.dumps(self._last_data))
            except Exception:
                pass
        try:
            await websocket.wait_closed()
        finally:
            self._clients.discard(websocket)

    async def _serve(self):
        async with websockets.serve(self._handler, "127.0.0.1", WS_PORT):
            print(f"[WebSocketServer] Listening on ws://127.0.0.1:{WS_PORT}")
            await asyncio.Future()

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._serve())

    def start(self):
        thread = threading.Thread(target=self._run_loop, daemon=True)
        thread.start()

    def broadcast(self, data: dict):
        self._last_data = data
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
