import asyncio
from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY


class ChatReader:
    def __init__(self, video_id: str):
        self.video_id = video_id
        self._youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    def _get_live_chat_id(self) -> str:
        resp = self._youtube.videos().list(
            part="liveStreamingDetails",
            id=self.video_id,
        ).execute()
        items = resp.get("items", [])
        if not items:
            raise ValueError(f"Video not found: {self.video_id}")
        details = items[0].get("liveStreamingDetails", {})
        chat_id = details.get("activeLiveChatId")
        if not chat_id:
            raise ValueError("No active live chat found. Is the stream live?")
        return chat_id

    async def read_messages(self):
        live_chat_id = self._get_live_chat_id()
        print(f"[ChatReader] Live chat ID: {live_chat_id}")

        page_token = None
        seen_ids: set[str] = set()

        while True:
            resp = self._youtube.liveChatMessages().list(
                liveChatId=live_chat_id,
                part="snippet,authorDetails",
                pageToken=page_token,
                maxResults=200,
            ).execute()

            for item in resp.get("items", []):
                msg_id = item["id"]
                if msg_id in seen_ids:
                    continue
                seen_ids.add(msg_id)

                snippet = item.get("snippet", {})
                if snippet.get("type") != "textMessageEvent":
                    continue

                yield {
                    "author": item["authorDetails"]["displayName"],
                    "message": snippet["displayMessage"],
                    "timestamp": snippet["publishedAt"],
                }

            page_token = resp.get("nextPageToken")
            poll_ms = resp.get("pollingIntervalMillis", 5000)
            await asyncio.sleep(poll_ms / 1000)
