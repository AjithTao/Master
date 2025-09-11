from bs4 import BeautifulSoup
import re

def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    return soup.get_text("\n").strip()

VIDEO_LINK_PATTERNS = [
    r'https?://[^\s]+teams\.microsoft\.com[^"]*',
    r'https?://[^\s]+sharepoint\.com[^"]*',
    r'https?://[^\s]*loom\.com[^"]*',
    r'https?://[^\s]*youtube\.com[^"]*',
    r'https?://youtu\.be/[^\s]+'
]

def extract_video_links(text: str) -> list[str]:
    links = []
    for pat in VIDEO_LINK_PATTERNS:
        links += re.findall(pat, text, flags=re.IGNORECASE)
    # De-dup while preserving order
    seen = set()
    dedup = []
    for l in links:
        if l not in seen:
            seen.add(l)
            dedup.append(l)
    return dedup
