"""Tests for crawler (unit only; no network)."""

import tempfile
from pathlib import Path

import pytest

from src.crawler import MANUS_SEED_URLS, slug_from_url


def test_slug_from_url():
    assert "00_" in slug_from_url("https://manus.im/", 0)
    assert "01_" in slug_from_url("https://manus.im/docs/welcome", 1)
    # No invalid path chars
    name = slug_from_url("https://example.com/path?query=1", 2)
    assert "/" not in name
    assert "?" not in name


def test_manus_seed_urls():
    assert len(MANUS_SEED_URLS) >= 1
    assert any("manus" in u.lower() for u in MANUS_SEED_URLS)


def test_crawl_brand_empty_urls_returns_empty_when_no_search():
    from src.crawler import crawl_brand

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        # Brand other than Manus, no urls, no search -> urls stay empty or from search
        saved = crawl_brand(
            "SomeOtherBrand", urls=[], output_dir=out, max_docs=2, use_search=False
        )
    assert saved == []
