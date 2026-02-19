"""
Crawl the web for real-life content about a brand (default: Manus) and save to data/documents/clean/.
Run from project root: python scripts/crawl_brand.py [--brand Manus] [--max-docs 5]
After crawling, run scripts/ingest_documents.py to rebuild ChromaDB with the new clean docs.

URL sources (in order of priority):
1. --urls command-line argument (overrides everything)
2. --seed-urls-file JSON config file
3. Built-in seed URLs for known brands (Manus)
4. DuckDuckGo search (unless --no-search is used)
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Make `src` importable when running `python scripts/crawl_brand.py` (e.g. in CI)
# without requiring an editable install.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Also set PYTHONPATH for any subprocesses started by this script.
import os

os.environ.setdefault("PYTHONPATH", str(PROJECT_ROOT))

from src.config import CLEAN_DIR, DOCUMENTS_JSON
from src.crawler import crawl_brand


def load_seed_urls_from_file(filepath: Path) -> dict[str, list[str]]:
    """
    Load brand seed URLs from a JSON config file.
    Expected format:
    {
      "Manus": ["https://manus.im/", "https://manus.im/docs/..."],
      "OtherBrand": ["https://example.com/"]
    }
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Warning: Could not load seed URLs from {filepath}: {e}")
        return {}


def main():
    p = argparse.ArgumentParser(
        description="Crawl web for brand content and save as clean docs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use specific URLs
  python scripts/crawl_brand.py --brand Manus --urls "https://manus.im/" "https://manus.im/docs/"

  # Use URLs from config file
  python scripts/crawl_brand.py --brand MyBrand --seed-urls-file data/seed_urls.json

  # Use only seed URLs (no search)
  python scripts/crawl_brand.py --brand Manus --no-search

  # Filter by sentiment
  python scripts/crawl_brand.py --brand Manus --min-sentiment 0
        """,
    )
    p.add_argument("--brand", default="Manus", help="Brand name (default: Manus)")
    p.add_argument(
        "--max-docs",
        type=int,
        default=5,
        help="Max number of clean docs to save (default: 5)",
    )
    p.add_argument(
        "--no-search",
        action="store_true",
        help="Only use seed URLs (no DuckDuckGo search)",
    )
    p.add_argument(
        "--urls",
        nargs="*",
        help="List of URLs to fetch (overrides seed URLs and search)",
    )
    p.add_argument(
        "--seed-urls-file",
        type=Path,
        help='Path to JSON file with brand seed URLs (format: {"Brand": ["url1", "url2"]})',
    )
    p.add_argument(
        "--min-sentiment",
        type=float,
        default=None,
        metavar="FLOAT",
        help=(
            "Only save pages with VADER compound sentiment >= this (e.g. 0 or -0.2). "
            "Use when real data is often negative."
        ),
    )
    p.add_argument(
        "--no-warn-negative",
        action="store_true",
        help="Do not warn when a crawled page is highly negative",
    )
    args = p.parse_args()

    # Determine URLs to use
    urls_to_crawl = None
    if args.urls:
        # Priority 1: Command-line URLs
        urls_to_crawl = args.urls
        print(f"Using {len(urls_to_crawl)} URLs from command line")
    elif args.seed_urls_file:
        # Priority 2: Seed URLs from config file
        seed_config = load_seed_urls_from_file(args.seed_urls_file)
        if args.brand in seed_config:
            urls_to_crawl = seed_config[args.brand]
            print(
                f"Using {len(urls_to_crawl)} seed URLs from {args.seed_urls_file} "
                f"for brand '{args.brand}'"
            )
        else:
            print(
                f"Warning: Brand '{args.brand}' not found in {args.seed_urls_file}, will use search"
            )

    # Prefer updating documents.json when it exists so a single file organises
    # all data
    output_json = DOCUMENTS_JSON if DOCUMENTS_JSON.exists() else None
    saved = crawl_brand(
        brand=args.brand,
        urls=urls_to_crawl,
        output_dir=CLEAN_DIR if output_json is None else None,
        output_json=output_json,
        max_docs=args.max_docs,
        use_search=not args.no_search,
        min_sentiment=args.min_sentiment,
        warn_negative=not args.no_warn_negative,
    )
    if output_json and saved:
        print(
            f"Updated {DOCUMENTS_JSON} with new clean content. Run ingest to rebuild ChromaDB."
        )
    else:
        print(f"Saved {len(saved)} documents to {CLEAN_DIR}")
    for path in saved:
        print(f"  - {path.name}")
    if saved:
        print("Next: run python scripts/ingest_documents.py to rebuild ChromaDB.")


if __name__ == "__main__":
    main()
