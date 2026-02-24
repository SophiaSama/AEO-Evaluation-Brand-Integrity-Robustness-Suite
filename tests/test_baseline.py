"""Tests for baseline helpers."""

from src import baseline


def test_get_baseline_queries_uses_brand():
    brand = "Acme"
    queries = baseline.get_baseline_queries(brand)
    assert len(queries) == 2
    assert all(brand in q for q in queries)


def test_get_baseline_response_defaults(monkeypatch):
    captured = {}

    def fake_query(question, use_clean_only):
        captured["question"] = question
        captured["use_clean_only"] = use_clean_only
        return "answer", ["ctx"]

    monkeypatch.setattr(baseline, "query_rag_with_context", fake_query)
    answer, contexts = baseline.get_baseline_response(brand="Acme")

    assert answer == "answer"
    assert contexts == ["ctx"]
    assert captured["use_clean_only"] is True
    assert captured["question"] == "What is Acme known for?"
