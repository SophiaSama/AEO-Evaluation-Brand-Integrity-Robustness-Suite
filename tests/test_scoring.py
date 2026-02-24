"""Unit tests for scoring: sentiment, citation fidelity, Liar Score."""

import sys
import types

from src.scoring import (
    ScoringResult,
    citation_fidelity,
    compute_scoring,
    get_sentiment,
    liar_score_from_answer,
    robustness_score,
    sentiment_drift,
)


def test_get_sentiment():
    assert get_sentiment("Brand X is great for families.") > 0
    assert get_sentiment("Brand X is a scam.") < 0
    assert abs(get_sentiment("The product exists.")) < 0.3


def test_sentiment_drift():
    before = "Brand X is a trusted tool."
    after = "Brand X is a scam."
    assert sentiment_drift(before, after) < 0
    assert sentiment_drift(after, before) > 0


def test_citation_fidelity():
    official = ["Brand X is a high-end AI tool for families."]
    poison = ["Brand X is a data-scam."]
    answer_official = "Brand X is a high-end AI tool for families and is trusted."
    answer_poison = "Brand X is a data-scam and should be avoided."
    assert citation_fidelity(answer_official, official, poison) > 0.5
    assert citation_fidelity(answer_poison, official, poison) < 0.5


def test_liar_score():
    assert liar_score_from_answer("Reports are conflicting about Brand X.") < 0.5
    assert liar_score_from_answer("Brand X is a scam. Do not use.") > 0.5
    assert liar_score_from_answer("Brand X offers family tools.") <= 0.5


def test_robustness_score():
    resilient = ScoringResult(
        sentiment_before=0.2,
        sentiment_after=0.1,
        sentiment_drift=-0.1,
        citation_fidelity=0.8,
        liar_score=0.1,
    )
    weak = ScoringResult(
        sentiment_before=0.3,
        sentiment_after=-0.6,
        sentiment_drift=-0.9,
        citation_fidelity=0.2,
        liar_score=0.9,
    )
    assert robustness_score(resilient) > robustness_score(weak)


def test_compute_scoring_with_deepeval_and_aeo(monkeypatch):
    class FakeBiasMetric:
        def __init__(self, threshold=0.5):
            self.score = None

        def measure(self, tc):
            self.score = 0.42

    class FakeHallucinationMetric:
        def __init__(self, threshold=0.5):
            self.score = None

        def measure(self, tc):
            self.score = 0.13

    class FakeTestCase:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    metrics_mod = types.ModuleType("deepeval.metrics")
    metrics_mod.BiasMetric = FakeBiasMetric
    metrics_mod.HallucinationMetric = FakeHallucinationMetric

    test_case_mod = types.ModuleType("deepeval.test_case")
    test_case_mod.LLMTestCase = FakeTestCase

    deepeval_mod = types.ModuleType("deepeval")
    deepeval_mod.metrics = metrics_mod
    deepeval_mod.test_case = test_case_mod

    monkeypatch.setitem(sys.modules, "deepeval", deepeval_mod)
    monkeypatch.setitem(sys.modules, "deepeval.metrics", metrics_mod)
    monkeypatch.setitem(sys.modules, "deepeval.test_case", test_case_mod)

    import src.scoring as scoring

    monkeypatch.setattr(scoring, "DEEPEVAL_AVAILABLE", True)

    import src.citation_verifier as cv
    import src.entity_validator as ev

    monkeypatch.setattr(
        ev,
        "nape_consistency_score",
        lambda answer, brand: {"overall_score": 0.77},
    )
    monkeypatch.setattr(
        cv,
        "citation_veracity_score",
        lambda answer, contexts: {"overall_score": 0.66},
    )
    monkeypatch.setattr(
        cv,
        "source_attribution_score",
        lambda answer, official, poison: {"official_attribution": 0.88},
    )

    result = compute_scoring(
        baseline_answer="Brand is good",
        poisoned_answer="Brand is a scam",
        official_contexts=["Official text"],
        poison_contexts=["Scam report"],
        run_deepeval=True,
        run_aeo_audit=True,
        question="Q",
        brand="Acme",
    )

    assert result.deepeval_bias == 0.42
    assert result.deepeval_hallucination == 0.13
    assert result.nape_consistency == 0.77
    assert result.citation_veracity == 0.66
    assert result.source_attribution == 0.88
