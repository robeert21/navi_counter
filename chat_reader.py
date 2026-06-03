import asyncio
import json
import re
import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
# YouTube's own web client API key (public, embedded in their web app)
_YT_API_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"


class ChatReader:
    def __init__(self, video_id: str):
        self.video_id = video_id
        self._session = requests.Session()
        self._session.headers.update(_HEADERS)

    def _get_continuation(self) -> str:
        resp = self._session.get(
            f"https://www.youtube.com/watch?v={self.video_id}",
            params={"hl": "en"},
            timeout=10,
        )
        match = re.search(r'"continuation"\s*:\s*"([^"]+)"', resp.text)
        if not match:
            raise ValueError("No active live chat found. Is the stream live?")
        return match.group(1)

    def _fetch(self, continuation: str) -> dict:
        resp = self._session.post(
            "https://www.youtube.com/youtubei/v1/live_chat/get_live_chat",
            params={"key": _YT_API_KEY},
            json={
                "context": {
                    "client": {
                        "clientName": "WEB",
                        "clientVersion": "2.20231121.09.00",
                    }
                },
                "continuation": continuation,
            },
            timeout=10,
        )
        return resp.json()

    async def read_messages(self):
        continuation = self._get_continuation()
        seen_ids: set[str] = set()

        while True:
            try:
                data = self._fetch(continuation)
                chat = data.get("continuationContents", {}).get("liveChatContinuation", {})

                # next continuation + poll interval
                timeout = 5.0
                for cont in chat.get("continuations", []):
                    for key in ("invalidationContinuationData", "timedContinuationData"):
                        if key in cont:
                            continuation = cont[key]["continuation"]
                            timeout = cont[key].get("timeoutMs", 5000) / 1000
                            break

                for action in chat.get("actions", []):
                    renderer = (
                        action.get("addChatItemAction", {})
                        .get("item", {})
                        .get("liveChatTextMessageRenderer", {})
                    )
                    if not renderer:
                        continue

                    msg_id = renderer.get("id", "")
                    if msg_id in seen_ids:
                        continue
                    seen_ids.add(msg_id)

                    runs = renderer.get("message", {}).get("runs", [])
                    message = "".join(r.get("text", "") for r in runs)
                    author = renderer.get("authorName", {}).get("simpleText", "")

                    if message:
                        yield {
                            "author": author,
                            "message": message,
                            "timestamp": renderer.get("timestampText", {}).get("simpleText", ""),
                        }

            except Exception as e:
                print(f"[ChatReader] Error: {e}")
                timeout = 5.0

            await asyncio.sleep(timeout)
