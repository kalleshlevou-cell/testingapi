"""Fetch and extract meaningful content from a website."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import httpx
from bs4 import BeautifulSoup


@dataclass
class WebsiteContent:
    """Structured representation of extracted website content."""

    url: str = ""
    title: str = ""
    meta_description: str = ""
    meta_keywords: str = ""
    headings: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    links: list[dict[str, str]] = field(default_factory=list)
    og_tags: dict[str, str] = field(default_factory=dict)
    body_text: str = ""
    raw_html_length: int = 0

    def to_prompt_text(self, max_chars: int = 50000) -> str:
        """Return a cleaned text representation suitable for an LLM prompt."""
        sections: list[str] = []
        sections.append(f"URL: {self.url}")
        if self.title:
            sections.append(f"Page Title: {self.title}")
        if self.meta_description:
            sections.append(f"Meta Description: {self.meta_description}")
        if self.meta_keywords:
            sections.append(f"Meta Keywords: {self.meta_keywords}")
        if self.og_tags:
            og_lines = [f"  {k}: {v}" for k, v in self.og_tags.items()]
            sections.append("Open Graph Tags:\n" + "\n".join(og_lines))
        if self.headings:
            sections.append(
                "Headings:\n" + "\n".join(f"  - {h}" for h in self.headings[:40])
            )
        if self.paragraphs:
            sections.append(
                "Key Paragraphs:\n"
                + "\n".join(f"  {p}" for p in self.paragraphs[:60])
            )
        if self.links:
            link_lines = [
                f"  {l.get('text', '')}: {l.get('href', '')}"
                for l in self.links[:30]
            ]
            sections.append("Links:\n" + "\n".join(link_lines))

        combined = "\n\n".join(sections)
        if len(combined) > max_chars:
            combined = combined[:max_chars] + "\n... [content truncated]"
        return combined


_STRIP_TAGS = {"script", "style", "noscript", "svg", "iframe", "canvas"}
_WHITESPACE_RE = re.compile(r"\s+")


async def extract_website_content(url: str, timeout: int = 30) -> WebsiteContent:
    """Fetch *url* and return structured WebsiteContent.

    Raises httpx.HTTPError on network/HTTP failures.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; LinkAnalysisBot/1.0; "
            "+https://github.com/ai-link-analysis)"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with httpx.AsyncClient(
        follow_redirects=True, timeout=timeout, verify=True
    ) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

    html = response.text
    soup = BeautifulSoup(html, "lxml")

    # Remove unwanted tags
    for tag in soup.find_all(_STRIP_TAGS):
        tag.decompose()

    content = WebsiteContent(url=url, raw_html_length=len(html))

    # Title
    if soup.title and soup.title.string:
        content.title = soup.title.string.strip()

    # Meta tags
    for meta in soup.find_all("meta"):
        name = (meta.get("name") or meta.get("property") or "").lower()
        value = (meta.get("content") or "").strip()
        if not value:
            continue
        if name == "description":
            content.meta_description = value
        elif name == "keywords":
            content.meta_keywords = value
        elif name.startswith("og:"):
            content.og_tags[name] = value

    # Headings
    for level in ("h1", "h2", "h3"):
        for tag in soup.find_all(level):
            text = _clean(tag.get_text())
            if text:
                content.headings.append(text)

    # Paragraphs
    for p in soup.find_all("p"):
        text = _clean(p.get_text())
        if len(text) > 20:
            content.paragraphs.append(text)

    # Links (navigation/internal)
    seen_hrefs: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        link_text = _clean(a.get_text())
        if href in seen_hrefs or not link_text:
            continue
        seen_hrefs.add(href)
        content.links.append({"text": link_text, "href": href})

    # Full body text (fallback)
    body = soup.find("body")
    if body:
        content.body_text = _clean(body.get_text())

    return content


def _clean(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text).strip()

