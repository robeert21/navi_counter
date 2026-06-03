import asyncio
import signal
import pytchat


class ChatReader:
    def __init__(self, video_id: str):
        self.video_id = video_id

    async def read_messages(self):
        # pytchat tries to register signal handlers which only work on the main
        # thread — temporarily replace signal.signal with a no-op to avoid the error
        original = signal.signal
        signal.signal = lambda *a, **kw: None
        try:
            chat = pytchat.create(video_id=self.video_id)
        finally:
            signal.signal = original

        if not chat.is_alive():
            raise ValueError("No active live chat found. Is the stream live?")

        while chat.is_alive():
            for item in chat.get().sync_items():
                yield {
                    "author": item.author.name,
                    "message": item.message,
                    "timestamp": item.datetime,
                }
            await asyncio.sleep(1)
