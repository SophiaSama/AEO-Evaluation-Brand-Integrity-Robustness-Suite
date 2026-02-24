"""Tests for crawler (unit only; no network)."""

import json
import tempfile
from pathlib import Path

import pytest

from src.crawler import MANUS_SEED_URLS, fetch_url, search_brand, slug_from_url


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
        # Brand other than Manus, no urls, no search -> urls stay empty or from
        # search
        saved = crawl_brand(
            "SomeOtherBrand", urls=[], output_dir=out, max_docs=2, use_search=False
        )
    assert saved == []


def test_crawl_brand_writes_json_and_dedup(monkeypatch, tmp_path):
    from src import crawler

    urls = ["https://example.com/1", "https://example.com/2"]

    def fake_fetch(url):
        return "Same content across two pages with enough length to pass. " * 6

    monkeypatch.setattr(crawler, "fetch_url", fake_fetch)
    monkeypatch.setattr(crawler, "_get_sentiment", lambda text: 0.1)
    monkeypatch.setattr(crawler.time, "sleep", lambda *_: None)

    output_json = tmp_path / "documents.json"
    saved = crawler.crawl_brand(
        "Acme",
        urls=urls,
        output_json=output_json,
        max_docs=5,
        use_search=False,
    )

    assert saved == [output_json]
    data = json.loads(output_json.read_text(encoding="utf-8"))
    assert len(data["clean"]) == 1


def test_fetch_url_request_error(monkeypatch):
    import src.crawler as crawler

    def fake_get(*args, **kwargs):
        raise crawler.requests.RequestException("boom")

    monkeypatch.setattr(crawler.requests, "get", fake_get)
    assert fetch_url("https://example.com") is None


def test_fetch_url_trafilatura_fallbacks(monkeypatch):
    import src.crawler as crawler

    class DummyResp:
        text = "<html><body>hello</body></html>"

        def raise_for_status(self):
            return None

    monkeypatch.setattr(crawler.requests, "get", lambda *a, **k: DummyResp())

    calls = {"count": 0}

    def fake_extract(html, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return None
        return "x" * 150

    monkeypatch.setattr(crawler.trafilatura, "extract", fake_extract)
    text = fetch_url("https://example.com")
    assert text is not None
    assert len(text) >= 100


def test_fetch_url_bs4_fallback(monkeypatch):
    import src.crawler as crawler

    class DummyResp:
        text = "<html><body>" + ("word " * 60) + "</body></html>"

        def raise_for_status(self):
            return None

    monkeypatch.setattr(crawler.requests, "get", lambda *a, **k: DummyResp())
    monkeypatch.setattr(crawler.trafilatura, "extract", lambda *a, **k: None)

    text = fetch_url("https://example.com")
    assert text is not None
    assert len(text) > 200


def test_search_brand_collects_urls(monkeypatch):
    import src.crawler as crawler

    class FakeDDGS:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def text(self, query, max_results):
            return [
                {"href": "https://a.example"},
                {"url": "https://b.example"},
                {"link": "https://c.example"},
            ]

    monkeypatch.setattr(crawler, "DDGS", FakeDDGS)
    urls = search_brand("Acme", num_results=3)
    assert urls == ["https://a.example", "https://b.example", "https://c.example"]


def test_crawl_brand_min_sentiment_filters(monkeypatch, tmp_path, capsys):
    from src import crawler

    def fake_fetch(url):
        return "content " * 40

    monkeypatch.setattr(crawler, "fetch_url", fake_fetch)
    monkeypatch.setattr(crawler, "_get_sentiment", lambda text: -0.6)
    monkeypatch.setattr(crawler.time, "sleep", lambda *_: None)

    saved = crawler.crawl_brand(
        "Acme",
        urls=["https://example.com"],
        output_dir=tmp_path,
        max_docs=1,
        use_search=False,
        min_sentiment=0.0,
    )

    assert saved == []
    output = capsys.readouterr().out
    assert "Skipped" in output


def test_crawl_brand_writes_text_files(monkeypatch, tmp_path):
    from src import crawler

    def fake_fetch(url):
        return "content " * 40

    monkeypatch.setattr(crawler, "fetch_url", fake_fetch)
    monkeypatch.setattr(crawler, "_get_sentiment", lambda text: 0.2)
    monkeypatch.setattr(crawler.time, "sleep", lambda *_: None)

    saved = crawler.crawl_brand(
        "Acme",
        urls=["https://example.com"],
        output_dir=tmp_path,
        max_docs=1,
        use_search=False,
    )

    assert len(saved) == 1
    assert saved[0].exists()


def test_crawl_brand_overwrites_clean_preserves_poison(monkeypatch, tmp_path):
    from src import crawler

    def fake_fetch(url):
        return "content " * 40

    monkeypatch.setattr(crawler, "fetch_url", fake_fetch)
    monkeypatch.setattr(crawler, "_get_sentiment", lambda text: 0.2)
    monkeypatch.setattr(crawler.time, "sleep", lambda *_: None)

    output_json = tmp_path / "documents.json"
    output_json.write_text(
        json.dumps({"clean": [], "poison": [{"id": "p1"}]}),
        encoding="utf-8",
    )

    crawler.crawl_brand(
        "Acme",
        urls=["https://example.com"],
        output_json=output_json,
        max_docs=1,
        use_search=False,
    )

    data = json.loads(output_json.read_text(encoding="utf-8"))
    assert len(data["clean"]) == 1
    assert data["poison"] == [{"id": "p1"}]
