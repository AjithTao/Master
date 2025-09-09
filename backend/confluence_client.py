import httpx
import logging
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class ConfluenceConfig:
    def __init__(self, base_url: str, email: str, api_token: str):
        # Confluence Cloud base will typically be https://<site>.atlassian.net/wiki
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.api_token = api_token


class ConfluenceClient:
    def __init__(self, cfg: ConfluenceConfig):
        self.cfg = cfg
        self._client: Optional[httpx.AsyncClient] = None

    async def initialize(self):
        if not self._client:
            auth = (self.cfg.email, self.cfg.api_token)
            timeout = httpx.Timeout(30.0, read=30.0)
            self._client = httpx.AsyncClient(auth=auth, timeout=timeout)

    async def close(self):
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass
            self._client = None

    def _headers(self) -> Dict[str, str]:
        return {"Accept": "application/json"}

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Confluence using CQL for full-text across pages."""
        if not self._client:
            await self.initialize()

        # Confluence Cloud search API
        url = f"{self.cfg.base_url}/rest/api/search"
        cql = f'text ~ "{query}"'
        params = {
            "cql": cql,
            "limit": str(limit),
        }
        try:
            resp = await self._client.get(url, params=params, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
            # Results contain content with id/type, and excerpt
            results = data.get("results", [])
            return results
        except Exception as e:
            logger.error(f"[Confluence] search failed: {e}")
            return []

    async def search_pages(self, title_query: str, space: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search pages by title (CQL)."""
        if not self._client:
            await self.initialize()

        url = f"{self.cfg.base_url}/rest/api/search"
        # Build CQL string
        parts = ["type = page"]
        if title_query:
            parts.append(f'title ~ "{title_query}"')
        if space:
            parts.append(f'space = "{space}"')
        cql = " AND ".join(parts)
        params = {"cql": cql, "limit": str(limit)}
        try:
            resp = await self._client.get(url, params=params, headers=self._headers())
            resp.raise_for_status()
            return resp.json().get("results", [])
        except Exception as e:
            logger.error(f"[Confluence] search_pages failed: {e}")
            return []

    @staticmethod
    def storage_html_to_text(storage_html: str) -> str:
        """Very simple HTML to text conversion for Confluence storage format."""
        try:
            import re, html
            # Replace <br/> and </p> with newlines
            text = storage_html.replace("<br/>", "\n").replace("<br>", "\n")
            text = re.sub(r"</p>", "\n\n", text)
            # Strip all remaining tags
            text = re.sub(r"<[^>]+>", "", text)
            # Unescape HTML entities
            text = html.unescape(text)
            # Normalize spaces
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            return text
        except Exception:
            return storage_html

    async def get_page(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get a Confluence page with storage format body."""
        if not self._client:
            await self.initialize()

        url = f"{self.cfg.base_url}/rest/api/content/{content_id}"
        params = {"expand": "body.storage,version,space"}
        try:
            resp = await self._client.get(url, params=params, headers=self._headers())
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"[Confluence] get_page failed for {content_id}: {e}")
            return None


