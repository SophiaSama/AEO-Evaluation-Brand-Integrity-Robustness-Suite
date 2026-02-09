"""Test visualization module."""

import json
from pathlib import Path

import pytest

from src.visualize import _get_overall_status, _get_status_class, generate_html_report


def test_get_status_class():
    """Test status class determination."""
    # Higher is better
    assert _get_status_class(0.8, threshold=0.5) == "pass"
    assert _get_status_class(0.3, threshold=0.5) == "fail"

    # Lower is better
    assert _get_status_class(0.2, threshold=0.5, lower_is_better=True) == "pass"
    assert _get_status_class(0.7, threshold=0.5, lower_is_better=True) == "fail"


def test_get_overall_status():
    """Test overall status calculation."""
    # All pass
    assert _get_overall_status({"test1": True, "test2": True}) == "pass"

    # Partial pass (80% threshold)
    assert (
        _get_overall_status(
            {"test1": True, "test2": False, "test3": True, "test4": True, "test5": True}
        )
        == "pass"
    )

    # Below threshold
    assert (
        _get_overall_status({"test1": True, "test2": False, "test3": False}) == "fail"
    )

    # Empty
    assert _get_overall_status({}) == ""


def test_generate_html_report(tmp_path):
    """Test HTML report generation."""
    # Create sample results
    sample_results = {
        "scoring": {
            "sentiment_before": 0.5,
            "sentiment_after": -0.2,
            "sentiment_drift": -0.7,
            "citation_fidelity": 0.8,
            "liar_score": 0.3,
        },
        "tests": {
            "BIRS-01": {"score": 0.85, "pass": True},
            "BIRS-02": {"score": 0.72, "pass": True},
            "BIRS-03": {"score": 0.45, "pass": False},
        },
    }

    # Save to temp file
    json_path = tmp_path / "test_results.json"
    with open(json_path, "w") as f:
        json.dump(sample_results, f)

    # Generate HTML
    html_path = generate_html_report(json_path)

    # Verify file was created
    assert html_path.exists()
    assert html_path.suffix == ".html"

    # Verify HTML content
    html_content = html_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html_content
    assert "BIRS Test Results" in html_content
    assert "Sentiment Drift" in html_content
    assert "Citation Fidelity" in html_content
    assert "Plotly" in html_content  # Chart library
    assert "BIRS-01" in html_content
    assert "BIRS-02" in html_content
    assert "BIRS-03" in html_content


def test_generate_html_report_custom_output(tmp_path):
    """Test HTML report with custom output path."""
    # Create sample results
    sample_results = {
        "scoring": {
            "sentiment_before": 0.3,
            "sentiment_after": 0.1,
            "sentiment_drift": -0.2,
            "citation_fidelity": 0.6,
            "liar_score": 0.5,
        },
        "tests": {"BIRS-01": {"score": 0.75, "pass": True}},
    }

    # Save to temp file
    json_path = tmp_path / "test_results.json"
    with open(json_path, "w") as f:
        json.dump(sample_results, f)

    # Generate HTML with custom output
    custom_output = tmp_path / "custom_report.html"
    html_path = generate_html_report(json_path, custom_output)

    # Verify custom path was used
    assert html_path == custom_output
    assert custom_output.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
