import asyncio
import json
import os
import signal

from chat_reader import ChatReader
from ai_classifier import AIClassifier
from ws_server import WebSocketServer
from config import YOUTUBE_VIDEO_ID

COUNTER_FILE = "counter.json"
BATCH_SIZE = 1


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


async def main():
    ws_server = WebSocketServer()
    ws_server.start()

    classifier = AIClassifier()
    reader = ChatReader(YOUTUBE_VIDEO_ID)

    count = load_counter()
    total_read = 0
    total_triggered = 0
    batch: list[dict] = []

    print(f"[Main] Starting. Loaded counter: {count}")

    try:
        async for msg in reader.read_messages():
            total_read += 1
            batch.append(msg)

            if len(batch) >= BATCH_SIZE:
                results = classifier.classify_batch(batch)

                for message, triggered in zip(batch, results):
                    if triggered:
                        count += 1
                        total_triggered += 1
                        save_counter(count)
                        ws_server.broadcast({
                            "count": count,
                            "last_author": message["author"],
                            "last_message": message["message"],
                        })
                        print(f"[NAVI] {message['author']}: \"{message['message']}\" | Total: {count}")

                batch.clear()

    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        # Flush remaining batch
        if batch:
            results = classifier.classify_batch(batch)
            for message, triggered in zip(batch, results):
                if triggered:
                    count += 1
                    total_triggered += 1
                    save_counter(count)
            batch.clear()

        save_counter(count)
        print(f"\n[Main] Stopped.")
        print(f"[Main] Total messages read : {total_read}")
        print(f"[Main] Total NAVI triggered: {total_triggered}")
        print(f"[Main] Final counter       : {count}")


if __name__ == "__main__":
    asyncio.run(main())
