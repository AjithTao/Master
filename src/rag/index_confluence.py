from __future__ import annotations
from typing import List, Dict, Any
from ..auth import ConfluenceConfig, LLMConfig
from ..confluence_client import ConfluenceClient
from .vectorstore import build_or_load_vs

def sync_space_to_vs(space_key: str, persist_dir: str) -> int:
    cfg = ConfluenceConfig()
    lcfg = LLMConfig()
    cli = ConfluenceClient(cfg)
    pages = cli.get_space_pages(space_key=space_key, limit=200)
    items = [cli.page_text_and_links(p) for p in pages]
    build_or_load_vs(items, persist_dir, lcfg.embeddings_model)
    return len(items)
