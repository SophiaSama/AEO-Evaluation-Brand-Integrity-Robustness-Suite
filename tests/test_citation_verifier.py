"""Unit tests for citation verifier helpers."""

import types

import src.citation_verifier as cv


def test_extract_claims_limits_and_length():
    text = (
        "This is a long factual sentence about the product. "
        "Another long sentence about features and benefits. "
        "Short. "
        "Third long sentence describing usage in detail. "
        "Fourth long sentence with more information. "
        "Fifth long sentence with additional facts. "
        "Sixth long sentence should be trimmed."
    )
    claims = cv.extract_claims(text)
    assert len(claims) == 5
    assert all(len(c) > 20 for c in claims)


def test_verify_citation_without_model(monkeypatch):
    monkeypatch.setattr(cv, "CROSS_ENCODER_AVAILABLE", False)
    result = cv.verify_citation("claim", "source")
    assert result["status"] == "ERROR"
    assert result["veracity_score"] == 0.5


def test_citation_veracity_score_without_model(monkeypatch):
    monkeypatch.setattr(cv, "CROSS_ENCODER_AVAILABLE", False)
    result = cv.citation_veracity_score("answer", ["context"])
    assert result["passed"] is False
    assert "error" in result


def test_detect_hallucinated_citations():
    answer = "According to Shadow Org, the system is unsafe."
    result = cv.detect_hallucinated_citations(answer, ["Official report text"])
    assert result["has_hallucination"] is True
    assert "Shadow Org" in result["hallucinated_sources"]


def test_source_attribution_without_model(monkeypatch):
    monkeypatch.setattr(cv, "CROSS_ENCODER_AVAILABLE", False)
    result = cv.source_attribution_score("answer", ["official"], ["poison"])
    assert result["passed"] is False
    assert result["official_attribution"] == 0.5


def test_verify_citation_with_model(monkeypatch):
    class DummyCE:
        def __init__(self, model_name):
            self.model_name = model_name

        def predict(self, pairs):
            return [0.1]

    monkeypatch.setattr(cv, "CROSS_ENCODER_AVAILABLE", True)
    monkeypatch.setitem(
        __import__("sys").modules,
        "sentence_transformers",
        types.SimpleNamespace(CrossEncoder=DummyCE),
    )

    result = cv.verify_citation("claim", "source")
    assert result["status"] == "VERIFIED"


def test_source_attribution_with_model(monkeypatch):
    class DummyCE:
        def __init__(self, model_name):
            self.model_name = model_name

        def predict(self, pairs):
            text = pairs[0][1]
            return [2.0] if "official" in text else [1.0]

    monkeypatch.setattr(cv, "CROSS_ENCODER_AVAILABLE", True)
    monkeypatch.setitem(
        __import__("sys").modules,
        "sentence_transformers",
        types.SimpleNamespace(CrossEncoder=DummyCE),
    )

    result = cv.source_attribution_score("answer", ["official info"], ["poison info"])
    assert result["passed"] is True
    assert result["official_attribution"] > result["poison_attribution"]


def test_extract_claims_no_long_sentences():
    claims = cv.extract_claims("Short. Tiny. Brief.")
    assert claims == []


def test_verify_citation_exception(monkeypatch):
    class DummyCE:
        def __init__(self, model_name):
            raise RuntimeError("boom")

    monkeypatch.setattr(cv, "CROSS_ENCODER_AVAILABLE", True)
    monkeypatch.setitem(
        __import__("sys").modules,
        "sentence_transformers",
        types.SimpleNamespace(CrossEncoder=DummyCE),
    )

    result = cv.verify_citation("claim", "source")
    assert result["status"] == "ERROR"
    assert "boom" in result["error"]


def test_citation_veracity_score_with_claims(monkeypatch):
    monkeypatch.setattr(cv, "CROSS_ENCODER_AVAILABLE", True)
    monkeypatch.setattr(
        cv, "verify_citation", lambda claim, source: {"status": "VERIFIED"}
    )

    answer = "This is a long sentence about features and benefits. Another long sentence about performance."
    result = cv.citation_veracity_score(answer, ["ctx"])
    assert result["passed"] is True
    assert result["claims_total"] > 0


def test_detect_hallucinated_citations_none():
    answer = "The product is safe and reliable."
    result = cv.detect_hallucinated_citations(answer, ["Official report text"])
    assert result["has_hallucination"] is False
