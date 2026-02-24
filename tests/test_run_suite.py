"""Unit tests for run_suite orchestration."""

from pathlib import Path

from src import run_suite as rs
from src.test_cases import TestResult


def test_run_suite_routes_contexts(monkeypatch, tmp_path):
    baseline_contexts = ["Official product overview."]
    poisoned_contexts = ["Official FAQ", "This is a scam report."]

    def fake_baseline_response(question, brand):
        return "baseline", baseline_contexts

    test_results = [
        TestResult(
            test_id="BIRS-01",
            name="Consensus Attack",
            passed=True,
            evidence="ok",
            raw_answer="poisoned",
            contexts=poisoned_contexts,
        )
    ]

    def fake_run_all_test_cases_extended(brand):
        return test_results

    captured = {}

    def fake_compute_scoring(**kwargs):
        captured.update(kwargs)
        return {"score": 1}

    def fake_save_results(**kwargs):
        return tmp_path / "results.json"

    def fake_generate_html_report(path: Path):
        return tmp_path / "report.html"

    monkeypatch.setattr(rs, "get_baseline_response", fake_baseline_response)
    monkeypatch.setattr(
        rs, "run_all_test_cases_extended", fake_run_all_test_cases_extended
    )
    monkeypatch.setattr(rs, "compute_scoring", fake_compute_scoring)
    monkeypatch.setattr(rs, "save_results", fake_save_results)

    import src.visualize as visualize

    monkeypatch.setattr(visualize, "generate_html_report", fake_generate_html_report)

    result = rs.run_suite(
        brand="Acme",
        output_dir=tmp_path,
        run_deepeval=False,
        run_aeo_audit=False,
        extended_tests=True,
        generate_html=True,
    )

    assert result == tmp_path / "results.json"
    assert captured["official_contexts"] == ["Official FAQ"]
    assert captured["poison_contexts"] == ["This is a scam report."]


def test_run_suite_non_extended_and_html_failure(monkeypatch, tmp_path):
    baseline_contexts = ["Official overview"]
    poisoned_contexts = ["Official FAQ", "This is a scam report."]

    def fake_baseline_response(question, brand):
        return "baseline", baseline_contexts

    test_results = [
        TestResult(
            test_id="BIRS-01",
            name="Consensus Attack",
            passed=True,
            evidence="ok",
            raw_answer="poisoned",
            contexts=poisoned_contexts,
        )
    ]

    def fake_run_all_test_cases(brand):
        return test_results

    def fake_compute_scoring(**kwargs):
        return {"score": 1}

    def fake_save_results(**kwargs):
        return tmp_path / "results.json"

    def fake_generate_html_report(path: Path):
        raise RuntimeError("fail html")

    monkeypatch.setattr(rs, "get_baseline_response", fake_baseline_response)
    monkeypatch.setattr(rs, "run_all_test_cases", fake_run_all_test_cases)
    monkeypatch.setattr(rs, "compute_scoring", fake_compute_scoring)
    monkeypatch.setattr(rs, "save_results", fake_save_results)

    import src.visualize as visualize

    monkeypatch.setattr(visualize, "generate_html_report", fake_generate_html_report)

    result = rs.run_suite(
        brand="Acme",
        output_dir=tmp_path,
        run_deepeval=False,
        run_aeo_audit=False,
        extended_tests=False,
        generate_html=True,
    )

    assert result == tmp_path / "results.json"
