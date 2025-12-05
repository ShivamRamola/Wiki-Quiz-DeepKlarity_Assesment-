import requests
from bs4 import BeautifulSoup


def _clean_text(node):
    return " ".join(node.get_text(separator=" ", strip=True).split())


def scrape_article(url: str) -> dict:
    """Fetches the given Wikipedia URL and extracts title, a short summary,
    top-level section headings, a list of linked entities (internal wiki links),
    and the raw HTML. Raises on non-200 responses.
    """
    headers = {"User-Agent": "wiki-quiz-scraper/1.0 (+https://example.com)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    html = resp.text
    soup = BeautifulSoup(html, "html.parser")

    # Title
    title_el = soup.find(id="firstHeading")
    title = _clean_text(title_el) if title_el else (soup.title.string if soup.title else "")

    # Main content area - fallback to body if not present
    content = soup.find(id="mw-content-text") or soup.find("body")

    # Summary: first meaningful <p>
    summary = ""
    if content:
        for p in content.find_all("p", recursive=True):
            text = _clean_text(p)
            if text and len(text) > 50:
                summary = text
                break

    # Sections: h2 and h3 headings within content
    sections = []
    if content:
        for header in content.find_all(["h2", "h3"]):
            htext = _clean_text(header)
            if htext:
                # Remove [edit] or similar bracketed text
                sections.append(htext.split("[", 1)[0].strip())

    # Entities: internal wiki links (filter out help, file, and meta links)
    entities = []
    if content:
        for a in content.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/wiki/") and ":" not in href:
                text = _clean_text(a)
                if text:
                    entities.append(text)

    # Deduplicate while preserving order
    seen = set()
    unique_entities = []
    for e in entities:
        if e not in seen:
            seen.add(e)
            unique_entities.append(e)

    return {
        "title": title,
        "summary": summary,
        "sections": sections,
        "entities": {"links": unique_entities},
        "raw_html": html,
    }
