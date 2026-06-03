import asyncio
import json
import os
import re
import sys
import threading
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler

from ws_server import WebSocketServer
from chat_reader import ChatReader
from ai_classifier import AIClassifier


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


_BASE = _base_dir()
COUNTER_FILE = str(_BASE / "counter.json")
BATCH_SIZE = 1
OVERLAY_DIR = str(_BASE / "overlay")
OVERLAY_PORT = 8766
OVERLAY_URL = f"http://127.0.0.1:{OVERLAY_PORT}"


def _start_overlay_server():
    handler = partial(SimpleHTTPRequestHandler, directory=OVERLAY_DIR)
    server = HTTPServer(("127.0.0.1", OVERLAY_PORT), handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()


def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|youtu\.be/|/live/)([A-Za-z0-9_-]{11})",
        r"(?:v=|youtu\.be/|/live/)([A-Za-z0-9_-]{10,12})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    stripped = url.strip()
    if re.match(r"^[A-Za-z0-9_-]{10,12}$", stripped):
        return stripped
    return ""


def load_counter() -> int:
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE) as f:
                return json.load(f).get("count", 0)
        except Exception:
            pass
    return 0


def save_counter(count: int):
    with open(COUNTER_FILE, "w") as f:
        json.dump({"count": count}, f)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NAVI Chat Monitor")
        self.resizable(False, False)
        self.configure(bg="#1a1a2e")

        _start_overlay_server()
        self._ws = WebSocketServer()
        self._ws.start()

        self._running = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._count = load_counter()
        self._ws.broadcast({"count": self._count})

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        BG = "#111111"
        ACCENT = "#F5D000"
        TEXT = "#cccccc"
        DIM = "#555555"
        RED = "#e05c5c"
        GREEN = "#4ade80"

        self._colors = {
            "bg": BG, "accent": ACCENT,
            "text": TEXT, "dim": DIM, "red": RED, "green": GREEN,
        }

        outer = tk.Frame(self, bg=BG, padx=24, pady=20)
        outer.pack()

        # ── Counter (dominant element)
        self._counter_lbl = tk.Label(
            outer, text=str(self._count),
            bg=BG, fg=ACCENT, font=("Arial Black", 72, "bold"),
        )
        self._counter_lbl.pack()

        # ── Last match
        self._last_lbl = tk.Label(
            outer, text="—", bg=BG, fg=DIM,
            font=("Arial", 10), wraplength=340, justify="center",
        )
        self._last_lbl.pack(pady=(0, 16))

        # ── URL input row
        input_row = tk.Frame(outer, bg=BG)
        input_row.pack(fill="x")

        self._url_var = tk.StringVar()
        self._url_entry = tk.Entry(
            input_row, textvariable=self._url_var,
            bg="#222222", fg=TEXT, insertbackground=TEXT,
            relief="flat", font=("Arial", 10), width=32,
        )
        self._url_entry.pack(side="left", ipady=7, padx=(0, 8))
        self._url_entry.bind("<Return>", lambda _: self._toggle())

        self._btn = tk.Button(
            input_row, text="START", command=self._toggle,
            bg=GREEN, fg="#000", font=("Arial Black", 9),
            relief="flat", padx=14, pady=7, cursor="hand2",
            activebackground="#22c55e",
        )
        self._btn.pack(side="left")

        tk.Button(
            input_row, text="↺", command=self._reset_counter,
            bg="#222222", fg=DIM, font=("Arial", 12),
            relief="flat", padx=8, pady=5, cursor="hand2",
            activebackground="#333333",
        ).pack(side="left", padx=(6, 0))

        # ── Status
        status_row = tk.Frame(outer, bg=BG)
        status_row.pack(fill="x", pady=(10, 0))

        self._status_dot = tk.Label(status_row, text="●", bg=BG, fg=DIM, font=("Arial", 10))
        self._status_dot.pack(side="left")
        self._status_lbl = tk.Label(status_row, text="oprit", bg=BG,
                                    fg=DIM, font=("Arial", 9))
        self._status_lbl.pack(side="left", padx=(4, 0))

        # ── Overlay URL (pentru OBS)
        overlay_row = tk.Frame(outer, bg=BG)
        overlay_row.pack(fill="x", pady=(6, 0))

        tk.Label(overlay_row, text="OBS URL:", bg=BG, fg=DIM,
                 font=("Arial", 8)).pack(side="left")

        overlay_lbl = tk.Label(overlay_row, text=OVERLAY_URL, bg=BG,
                               fg=ACCENT, font=("Arial", 8), cursor="hand2")
        overlay_lbl.pack(side="left", padx=(4, 0))

        def _copy_url(_event=None):
            self.clipboard_clear()
            self.clipboard_append(OVERLAY_URL)

        overlay_lbl.bind("<Button-1>", _copy_url)

    # ------------------------------------------------------------------ Actions

    def _reset_counter(self):
        self._count = 0
        save_counter(0)
        self._counter_lbl.config(text="0")
        self._last_lbl.config(text="—")

    def _toggle(self):
        if self._running:
            self._stop()
        else:
            self._start()

    def _start(self):
        url = self._url_var.get().strip()
        video_id = extract_video_id(url)
        if not video_id:
            self._set_status("URL invalid.", error=True)
            return

        os.environ["YOUTUBE_VIDEO_ID"] = video_id
        self._running = True
        self._btn.config(text="STOP", bg=self._colors["red"],
                         activebackground="#c04040")
        self._set_status(f"live · {video_id}", ok=True)

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _stop(self):
        self._running = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        self._btn.config(text="START", bg=self._colors["green"],
                         activebackground="#22c55e")
        self._set_status("oprit.")

    def _on_close(self):
        self._running = False
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self.quit()
        self.destroy()

    # ------------------------------------------------------------------ Async loop

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._monitor())
        except Exception:
            pass
        finally:
            self._loop.close()

    async def _monitor(self):
        video_id = os.environ.get("YOUTUBE_VIDEO_ID", "")
        reader = ChatReader(video_id)
        classifier = AIClassifier()
        batch = []

        try:
            async for msg in reader.read_messages():
                if not self._running:
                    break
                batch.append(msg)

                if len(batch) >= BATCH_SIZE:
                    results = classifier.classify_batch(batch)
                    for message, triggered in zip(batch, results):
                        if triggered:
                            self._count += 1
                            save_counter(self._count)
                            self._ws.broadcast({
                                "count": self._count,
                                "last_author": message["author"],
                                "last_message": message["message"],
                            })
                            self.after(0, self._on_hit, message)
                    batch.clear()
        except Exception as e:
            self.after(0, self._set_status, f"eroare: {e}", False, True)
            self._running = False
            self.after(0, lambda: self._btn.config(
                text="START", bg=self._colors["green"],
                activebackground="#22c55e"))

    # ------------------------------------------------------------------ UI updates

    def _on_hit(self, message: dict):
        self._counter_lbl.config(text=str(self._count))
        preview = message["message"][:60]
        self._last_lbl.config(text=f"{message['author']}: {preview}")

    def _set_status(self, text: str, ok=False, error=False):
        color = (self._colors["green"] if ok
                 else self._colors["red"] if error
                 else self._colors["dim"])
        self._status_dot.config(fg=color)
        self._status_lbl.config(text=text, fg=color)


if __name__ == "__main__":
    app = App()
    app.mainloop()
