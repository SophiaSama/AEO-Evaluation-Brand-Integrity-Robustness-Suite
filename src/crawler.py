"""
Crawl the web for real-life content about a brand (e.g. Manus).
Fetches URLs, extracts main text, and saves to data/documents/clean/ for use as "truthful" docs.
Respects rate limits and uses trafilatura for clean article extraction.

If real search results are mostly negative (bad press, complaints), "clean" would no longer
represent positive/neutral truth and BIRS metrics become hard to interpret. Use min_sentiment
to only keep neutral/positive pages, or use the bundled synthetic clean docs for a controlled test.
"""

import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
import trafilatura
from duckduckgo_search import DDGS
from vaderSentiment.vaderSentiment import (
    SentimentIntensityAnalyzer,  # type: ignore[import-untyped]
)

from src.config import CLEAN_DIR

_sentiment_analyzer = None


def _get_sentiment(text: str) -> float:
    """Compound sentiment in [-1, 1]. Cached analyzer."""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentIntensityAnalyzer()
    return _sentiment_analyzer.polarity_scores(text)["compound"]


# Default seed URLs for known brands (can be overridden via config file or
# command-line)
BRAND_SEED_URLS = {
    "manus": [
        "https://manus.im/",
        "https://manus.im/docs/introduction/welcome",
        "https://manus.ai/",
    ],
    # Add more brands here or use data/seed_urls.json via --seed-urls-file
}

# Legacy constant for backward compatibility
MANUS_SEED_URLS = BRAND_SEED_URLS["manus"]

USER_AGENT = "BIRS-Crawler/1.0 (Brand Integrity Robustness Suite; research)"
REQUEST_TIMEOUT = 15
DELAY_BETWEEN_REQUESTS = 1.0


def fetch_url(url: str) -> str | None:
    """
    Fetch URL and extract main text using trafilatura.
    Returns None on failure or if no meaningful text.
    """
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        resp.raise_for_status()
        html = resp.text
    except requests.RequestException:
        return None

    # Prefer trafilatura (strips nav/ads)
    text = trafilatura.extract(html, include_comments=False, include_tables=False)
    if text and len(text.strip()) > 200:
        return text.strip()

    # Fallback: get body text via trafilatura's fallback
    text = trafilatura.extract(html, no_fallback=False)
    if text and len(text.strip()) > 100:
        return text.strip()
    return None


def search_brand(brand: str, num_results: int = 10) -> list[str]:
    """
    Search DuckDuckGo for pages about the brand. Returns list of URLs.
    No API key required.
    """
    urls = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(f"{brand} AI", max_results=num_results):
                u = r.get("href")
                if u and u.startswith("http"):
                    urls.append(u)
    except Exception:
        pass
    return urls


def slug_from_url(url: str, index: int) -> str:
    """Generate a safe filename from URL."""
    parsed = urlparse(url)
    netloc = re.sub(r"[^\w.-]", "_", parsed.netloc or "unknown")
    path = re.sub(r"[^\w.-]", "_", (parsed.path or "")[:50])
    return f"{index:02d}_{netloc}{path}"[:60] or f"{index:02d}_page"


def crawl_brand(
    brand: str,
    urls: list[str] | None = None,
    output_dir: Path | None = None,
    output_json: Path | None = None,
    max_docs: int = 5,
    use_search: bool = True,
    min_sentiment: float | None = None,
    warn_negative: bool = True,
) -> list[Path]:
    """
    Crawl the web for content about the brand. If output_json is set (e.g. DOCUMENTS_JSON),
    updates the "clean" array in that JSON file; otherwise saves as .txt in output_dir (default: CLEAN_DIR).
    Returns list of saved paths (or [output_json] when writing to JSON).

    If real data is mostly negative (e.g. bad press), "clean" would skew baseline and metrics.
    - min_sentiment: If set (e.g. 0 or -0.2), only save docs with compound sentiment >= this value.
    - warn_negative: If True, print a warning when a fetched doc is highly negative (compound < -0.3).
    """
    if output_json is None:
        output_dir = output_dir or CLEAN_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = None

    if urls is None:
        # Check if brand has predefined seed URLs
        brand_key = brand.lower()
        if brand_key in BRAND_SEED_URLS:
            urls = list(BRAND_SEED_URLS[brand_key])
        else:
            urls = []
        if use_search and len(urls) < max_docs:
            found = search_brand(brand, num_results=max_docs + 5)
            for u in found:
                if u not in urls:
                    urls.append(u)
                if len(urls) >= max_docs + 5:
                    break
        urls = urls[: max_docs + 5]

    clean_entries: list[dict] = []
    skipped_negative = 0
    for i, url in enumerate(urls):
        if len(clean_entries) >= max_docs:
            break
        time.sleep(DELAY_BETWEEN_REQUESTS)
        text = fetch_url(url)
        if not text or len(text) < 150:
            continue

        # Sentiment: optional filter and/or warning when real data is negative
        compound = _get_sentiment(text)
        if min_sentiment is not None and compound < min_sentiment:
            skipped_negative += 1
            continue
        if warn_negative and compound < -0.3:
            print(
                (
                    f"  [warn] Negative content (sentiment {compound:.2f}) from "
                    f"{url[:60]}... — consider --min-sentiment to filter"
                )
            )

        # Truncate to ~15k chars per doc to keep chunks manageable
        if len(text) > 15000:
            text = text[:15000] + "\n\n[Content truncated for length.]"
        source = slug_from_url(url, len(clean_entries))
        clean_entries.append(
            {
                "id": source,
                "source": source + ".txt",
                "source_name": "official",
                "content": text,
            }
        )

    if skipped_negative and min_sentiment is not None:
        print(
            f"  [info] Skipped {skipped_negative} page(s) with sentiment below {min_sentiment}."
        )

    if output_json is not None and clean_entries:
        import json

        data = {"clean": clean_entries, "poison": []}
        if output_json.exists():
            data = json.loads(output_json.read_text(encoding="utf-8"))
            data["clean"] = clean_entries
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return [output_json]
    elif output_json is None and clean_entries:
        output_dir = output_dir or CLEAN_DIR
        saved = []
        for i, entry in enumerate(clean_entries):
            name = entry["source"]
            path = output_dir / name
            path.write_text(entry["content"], encoding="utf-8")
            saved.append(path)
        return saved
    return []
