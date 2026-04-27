from urllib.parse import urlparse
import httpx, asyncio, logging

from utils.constants import JINA_BASE, JUNK_SIGNALS, BLOCKED_DOMAINS, MIN_CONTENT_LENGTH

logger = logging.getLogger(__name__)


class JinaExtractorClient:

    def is_blocked_domains(self, url: str) -> bool:
        domain = (urlparse(url).hostname or "").lower()
        if not domain:
            return False

        return any(
            [
                block == domain or domain.endswith("." + block)
                for block in BLOCKED_DOMAINS
            ]
        )

    def _is_valid_content(self, url: str, text: str) -> bool:
        if len(text.strip()) < MIN_CONTENT_LENGTH or self.is_blocked_domains(url):
            logger.warning(f"⚠️ Too short ({len(text)} chars): {url[:60]}")
            return False

        # Check first 1000 chars only — 404 signals appear early
        sample = text[:1000].lower()
        for signal in JUNK_SIGNALS:
            if signal in sample:
                logger.warning(f"⚠️ Junk content detected ('{signal}'): {url[:60]}")
                return False

        return True

    async def fetch_jina(self, client, url):
        for attempt in range(3):
            try:
                resp = await client.get(JINA_BASE + url, timeout=20)
                if resp.status_code == 200:
                    if not self._is_valid_content(url, resp.text):
                        return url, None
                    logger.info(f"✅ Scraped: {url[:60]}...")
                    return url, resp.text
                elif resp.status_code == 429:
                    wait = 2 ** (attempt + 2)
                    logger.warning(f"⚠️ Rate limited: {url[:60]}, waiting {wait}s")
                    await asyncio.sleep(wait)
                else:
                    logger.warning(f"❌ HTTP {resp.status_code}: {url[:60]}")
                    return url, None
            except httpx.TimeoutException:
                logger.warning(f"⏰ Timeout attempt {attempt+1}: {url[:60]}")
                await asyncio.sleep(2**attempt)
            except Exception as e:
                logger.error(f"🔥 Error scraping {url[:60]}: {e}")
                return url, None
        return url, None

    async def process_urls(self, search_results):
        limits = httpx.Limits(max_connections=5, max_keepalive_connections=3)

        async with httpx.AsyncClient(limits=limits) as client:
            tasks = [self.fetch_jina(client, res["url"]) for res in search_results]
            response = await asyncio.gather(*tasks)
            return dict(response)
