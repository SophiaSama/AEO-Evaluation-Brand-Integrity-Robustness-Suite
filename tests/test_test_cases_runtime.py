"""Runtime tests for BIRS test case functions using mocked RAG."""

from src import test_cases


def test_run_birs_01_passes_on_conflict(monkeypatch):
    def fake_query(question, use_clean_only):
        return "Reports are conflicting about the brand.", ["ctx"]

    monkeypatch.setattr(test_cases, "query_rag_with_context", fake_query)
    result = test_cases.run_birs_01("Acme")
    assert result.passed is True


def test_run_birs_02_fails_on_liar(monkeypatch):
    def fake_query(question, use_clean_only):
        return "Brand X is a scam and unsafe.", ["ctx"]

    monkeypatch.setattr(test_cases, "query_rag_with_context", fake_query)
    result = test_cases.run_birs_02("Acme")
    assert result.passed is False


def test_run_birs_03_refusal_passes(monkeypatch):
    def fake_query(question, use_clean_only):
        return "I have no record of a 2025 leak.", ["ctx"]

    monkeypatch.setattr(test_cases, "query_rag_with_context", fake_query)
    result = test_cases.run_birs_03("Acme")
    assert result.passed is True


def test_run_all_test_cases_uses_helpers(monkeypatch):
    from src.test_cases import TestResult

    def fake_result(test_id):
        return TestResult(test_id, "name", True, "ok", "answer", ["ctx"])

    monkeypatch.setattr(test_cases, "run_birs_01", lambda brand: fake_result("BIRS-01"))
    monkeypatch.setattr(test_cases, "run_birs_02", lambda brand: fake_result("BIRS-02"))
    monkeypatch.setattr(test_cases, "run_birs_03", lambda brand: fake_result("BIRS-03"))

    results = test_cases.run_all_test_cases("Acme")
    assert [r.test_id for r in results] == ["BIRS-01", "BIRS-02", "BIRS-03"]


def test_run_all_test_cases_extended_uses_helpers(monkeypatch):
    from src.test_cases import TestResult

    def fake_result(test_id):
        return TestResult(test_id, "name", True, "ok", "answer", ["ctx"])

    monkeypatch.setattr(test_cases, "run_birs_01", lambda brand: fake_result("BIRS-01"))
    monkeypatch.setattr(test_cases, "run_birs_02", lambda brand: fake_result("BIRS-02"))
    monkeypatch.setattr(test_cases, "run_birs_03", lambda brand: fake_result("BIRS-03"))
    monkeypatch.setattr(test_cases, "run_birs_04", lambda brand: fake_result("BIRS-04"))
    monkeypatch.setattr(test_cases, "run_birs_05", lambda brand: fake_result("BIRS-05"))
    monkeypatch.setattr(test_cases, "run_birs_06", lambda brand: fake_result("BIRS-06"))

    results = test_cases.run_all_test_cases_extended("Acme")
    assert [r.test_id for r in results] == [
        "BIRS-01",
        "BIRS-02",
        "BIRS-03",
        "BIRS-04",
        "BIRS-05",
        "BIRS-06",
    ]


def test_run_birs_04_nape_passes_without_fake(monkeypatch):
    def fake_query(question, use_clean_only):
        return "Answer text", ["ctx"]

    monkeypatch.setattr(test_cases, "query_rag_with_context", fake_query)

    import src.entity_validator as ev

    monkeypatch.setattr(
        ev,
        "nape_consistency_score",
        lambda answer, brand: {"passed": True, "overall_score": 0.8},
    )
    monkeypatch.setattr(
        ev,
        "detect_fake_entities",
        lambda answer: {"has_fake": False, "fake_patterns": []},
    )

    result = test_cases.run_birs_04("Acme")
    assert result.passed is True
    assert "NAP+E" in result.evidence


def test_run_birs_04_fails_on_fake_entities(monkeypatch):
    def fake_query(question, use_clean_only):
        return "Answer text", ["ctx"]

    monkeypatch.setattr(test_cases, "query_rag_with_context", fake_query)

    import src.entity_validator as ev

    monkeypatch.setattr(
        ev,
        "nape_consistency_score",
        lambda answer, brand: {"passed": True, "overall_score": 0.9},
    )
    monkeypatch.setattr(
        ev,
        "detect_fake_entities",
        lambda answer: {"has_fake": True, "fake_patterns": ["fake address"]},
    )

    result = test_cases.run_birs_04("Acme")
    assert result.passed is False
    assert "fake" in result.evidence.lower()


def test_run_birs_05_handles_veracity_error(monkeypatch):
    def fake_query(question, use_clean_only):
        return "Answer text", ["ctx"]

    monkeypatch.setattr(test_cases, "query_rag_with_context", fake_query)

    import src.citation_verifier as cv

    monkeypatch.setattr(
        cv,
        "citation_veracity_score",
        lambda answer, contexts: {"error": "missing model"},
    )

    result = test_cases.run_birs_05("Acme")
    assert result.passed is False
    assert "Error" in result.evidence


def test_run_birs_06_attribution(monkeypatch):
    def fake_query(question, use_clean_only):
        return "Answer text", ["official context", "scam warning"]

    monkeypatch.setattr(test_cases, "query_rag_with_context", fake_query)

    import src.citation_verifier as cv

    monkeypatch.setattr(
        cv,
        "source_attribution_score",
        lambda answer, official, poison: {
            "passed": True,
            "official_attribution": 0.8,
            "poison_attribution": 0.2,
        },
    )

    result = test_cases.run_birs_06("Acme")
    assert result.passed is True
    assert "official" in result.evidence.lower()
