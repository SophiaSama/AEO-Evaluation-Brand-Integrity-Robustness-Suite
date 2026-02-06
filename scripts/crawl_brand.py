"""
Crawl the web for real-life content about a brand (default: Manus) and save to data/documents/clean/.
Run from project root: python scripts/crawl_brand.py [--brand Manus] [--max-docs 5]
After crawling, run scripts/ingest_documents.py to rebuild ChromaDB with the new clean docs.
"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CLEAN_DIR, DOCUMENTS_JSON
from src.crawler import crawl_brand


def main():
    p = argparse.ArgumentParser(description="Crawl web for brand content and save as clean docs.")
    p.add_argument("--brand", default="Manus", help="Brand name (default: Manus)")
    p.add_argument("--max-docs", type=int, default=5, help="Max number of clean docs to save (default: 5)")
    p.add_argument("--no-search", action="store_true", help="Only use seed URLs (no DuckDuckGo search)")
    p.add_argument("--urls", nargs="*", help="Optional list of URLs to fetch (overrides seed/search)")
    p.add_argument(
        "--min-sentiment",
        type=float,
        default=None,
        metavar="FLOAT",
        help="Only save pages with VADER compound sentiment >= this (e.g. 0 or -0.2). Use when real data is often negative.",
    )
    p.add_argument("--no-warn-negative", action="store_true", help="Do not warn when a crawled page is highly negative")
    args = p.parse_args()

    # Prefer updating documents.json when it exists so a single file organises all data
    output_json = DOCUMENTS_JSON if DOCUMENTS_JSON.exists() else None
    saved = crawl_brand(
        brand=args.brand,
        urls=args.urls if args.urls else None,
        output_dir=CLEAN_DIR if output_json is None else None,
        output_json=output_json,
        max_docs=args.max_docs,
        use_search=not args.no_search,
        min_sentiment=args.min_sentiment,
        warn_negative=not args.no_warn_negative,
    )
    if output_json and saved:
        print(f"Updated {DOCUMENTS_JSON} with new clean content. Run ingest to rebuild ChromaDB.")
    else:
        print(f"Saved {len(saved)} documents to {CLEAN_DIR}")
    for path in saved:
        print(f"  - {path.name}")
    if saved:
        print("Next: run python scripts/ingest_documents.py to rebuild ChromaDB.")


if __name__ == "__main__":
    main()
