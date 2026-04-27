from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SourcePlatform:
    name: str
    platform_type: str
    platform_id: str
    created_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None


@dataclass
class SourceContent:
    source_id: int
    platform_content_id: str
    title: str
    content: str
    content_url: str
    content_hash: str
    fetched_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None


@dataclass
class ContentSummary:
    content_id: int
    summary: str
    strategy_used: str  # "stuff" or "map_reduce"
    created_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
