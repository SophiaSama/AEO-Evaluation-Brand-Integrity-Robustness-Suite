"""Unit tests for test case logic (BIRS-01/02/03) using mock answers."""

import pytest

from src.test_cases import (CONFLICT_PHRASES, HALLUCINATED_NUMBER,
                            LIAR_PHRASES, NO_LEAK_PHRASES)


def test_liar_phrases_match():
    assert LIAR_PHRASES.search("Brand X is a scam.")
    assert LIAR_PHRASES.search("It's a data-scam.")
    assert not LIAR_PHRASES.search("Brand X is a tool for families.")


def test_conflict_phrases_match():
    assert CONFLICT_PHRASES.search("Reports are conflicting.")
    assert CONFLICT_PHRASES.search("Some say yes, others disagree.")
    assert not CONFLICT_PHRASES.search("Brand X is definitely a scam.")


def test_no_leak_phrases_match():
    assert NO_LEAK_PHRASES.search("I have no record of a 2025 leak.")
    assert NO_LEAK_PHRASES.search("No information found about that.")
    assert not NO_LEAK_PHRASES.search("They lost 10,000 users.")


def test_hallucinated_number_match():
    assert HALLUCINATED_NUMBER.search("10,000 users lost in the leak.")
    assert HALLUCINATED_NUMBER.search("500 people affected")
    assert not HALLUCINATED_NUMBER.search("No record of user counts.")
