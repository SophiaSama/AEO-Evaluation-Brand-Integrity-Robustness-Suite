"""Unit tests for scoring: sentiment, citation fidelity, Liar Score."""

from src.scoring import (
    ScoringResult,
    citation_fidelity,
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
