from datetime import datetime
from abc import ABC, abstractmethod
from typing import List
from storage.models import SourceContent


class BaseSourceAdapter(ABC):
    @abstractmethod
    async def fetch_latest(self, since: datetime) -> List[SourceContent] | None:
        """Fetch latest items"""
