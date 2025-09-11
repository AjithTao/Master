from __future__ import annotations
import requests
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from .auth import ConfluenceConfig
from .utils import html_to_text, extract_video_links

@dataclass
class ConfluenceClient:
    cfg: ConfluenceConfig

    def _auth(self):
        return (self.cfg.email, self.cfg.api_token)

    def _url(self, path: str) -> str:
        return f"{self.cfg.base_url}{path}"

    def search(self, cql: str, limit: int = 10) -> Dict[str, Any]:
        # Cloud: /wiki/rest/api/search?cql=...
        url = self._url("/rest/api/search")
        params = {"cql": cql, "limit": limit}
        r = requests.get(url, params=params, auth=self._auth(), timeout=60)
        r.raise_for_status()
        return r.json()

    def get_page(self, page_id: str) -> Dict[str, Any]:
        url = self._url(f"/rest/api/content/{page_id}")
        params = {"expand": "body.storage,version,metadata.labels"}
        r = requests.get(url, params=params, auth=self._auth(), timeout=60)
        r.raise_for_status()
        return r.json()

    def get_space_pages(self, space_key: str, limit: int = 100) -> List[Dict[str, Any]]:
        url = self._url("/rest/api/content")
        params = {
            "spaceKey": space_key,
            "type": "page",
            "limit": 50,
            "expand": "body.storage,version,metadata.labels"
        }
        results = []
        next_url = url
        while next_url and len(results) < limit:
            r = requests.get(next_url, params=params, auth=self._auth(), timeout=60)
            r.raise_for_status()
            data = r.json()
            results.extend(data.get("results", []))
            next_url = data.get("_links", {}).get("next")
            if next_url:
                next_url = self.cfg.base_url + next_url
            params = {}  # after first page the 'next' already has params
        return results[:limit]

    def page_text_and_links(self, page: Dict[str, Any]) -> Dict[str, Any]:
        title = page.get("title", "")
        page_id = page.get("id", "")
        body_html = page.get("body", {}).get("storage", {}).get("value", "")
        text = html_to_text(body_html)
        links = extract_video_links(body_html + "\n" + text)
        url = f"{self.cfg.base_url}/spaces/{page.get('space',{}).get('key','')}/pages/{page_id}"
        return {"id": page_id, "title": title, "url": url, "text": text, "video_links": links}
