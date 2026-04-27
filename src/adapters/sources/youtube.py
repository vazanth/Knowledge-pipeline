from datetime import datetime, timezone
import hashlib, asyncio, feedparser
from typing import Any, List
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)
from adapters.sources.base import BaseSourceAdapter
from storage.models import SourceContent


class YoutubeAdapter(BaseSourceAdapter):

    def __init__(self, local_id, platform_id):
        self.local_id = local_id
        self.platform_id = platform_id
        self.rss_url = (
            f"https://www.youtube.com/feeds/videos.xml?channel_id={platform_id}"
        )

    async def fetch_latest(self, since: datetime) -> List[SourceContent] | None:
        raw_feed: Any = await asyncio.to_thread(feedparser.parse, self.rss_url)
        new_content: List[SourceContent] = []

        if not hasattr(raw_feed, "entries") or not raw_feed.entries:
            print(f"⚠️ No entries found for channel {self.platform_id}")
            return new_content

        for entry in raw_feed.entries:
            if not hasattr(entry, "published_parsed"):
                continue

            published_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            if published_dt > since:
                video_id = getattr(entry, "yt_videoid", None)
                if not video_id:
                    continue
                transcript = await _get_transcript(video_id)

                if transcript:
                    clean_transcript = transcript.strip().lower()
                    clean_title = entry.title.strip().lower()
                    raw_string = f"{clean_title}|{clean_transcript}"
                    content_hash = hashlib.sha256(
                        raw_string.encode("utf-8")
                    ).hexdigest()
                    new_content.append(
                        SourceContent(
                            source_id=self.local_id,
                            platform_content_id=video_id,
                            content=transcript,
                            title=entry.title,
                            content_url=entry.link,
                            fetched_at=datetime.now(),
                            content_hash=content_hash,
                        )
                    )

        return new_content


async def _get_transcript(video_id: str) -> str | None:
    try:
        youtubeApi = YouTubeTranscriptApi()
        transcript_list = await asyncio.to_thread(youtubeApi.fetch, video_id)
        return " ".join([t.text for t in transcript_list.snippets])
    except (TranscriptsDisabled, NoTranscriptFound):
        print(f"⚠️ Captions unavailable for {video_id}. Skipping.")
        return None
