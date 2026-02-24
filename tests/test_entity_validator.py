"""Unit tests for entity validation helpers."""

import json

import src.entity_validator as ev


def test_load_ground_truth_reads_file(tmp_path, monkeypatch):
    data = {"Acme": {"name": "Acme", "official_name": "Acme Inc"}}
    path = tmp_path / "brands.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(ev, "GROUND_TRUTH_FILE", path)

    assert ev.load_ground_truth("Acme") == data["Acme"]


def test_fuzzy_match_handles_empty():
    assert ev.fuzzy_match("", "abc") == 0.0
    assert ev.fuzzy_match("abc", "") == 0.0


def test_extract_phone_numbers_and_emails_and_addresses():
    text = (
        "Call +65 6123 4567 or (123) 456-7890. "
        "Email support@example.com. "
        "Visit 10 Anson Road for details."
    )
    phones = ev.extract_phone_numbers(text)
    emails = ev.extract_emails(text)
    addresses = ev.extract_addresses(text)

    assert "+65 6123 4567" in phones
    assert "(123) 456-7890" in phones
    assert "support@example.com" in emails
    assert any("Anson Road" in addr for addr in addresses)


def test_validate_phone_expected_but_missing():
    ground = {"phone": "+65 6123 4567"}
    result = ev.validate_phone("No phone provided.", ground)
    assert result["passed"] is True
    assert result["score"] == 0.0


def test_detect_fake_entities():
    result = ev.detect_fake_entities("Our address is 123 Fake Street.")
    assert result["has_fake"] is True
    assert "fake address" in result["fake_patterns"]


def test_nape_consistency_no_ground_truth(monkeypatch):
    monkeypatch.setattr(ev, "load_ground_truth", lambda brand: None)
    result = ev.nape_consistency_score("answer", "Acme")
    assert result["passed"] is False
    assert "error" in result


def test_validate_name_email_address_and_nape(monkeypatch, tmp_path):
    answer = (
        "Acme Inc is located at 10 Anson Road in Singapore. "
        "Call +65 6123 4567 or email support@acme.com."
    )
    data = {
        "Acme": {
            "name": "Acme",
            "official_name": answer,
            "address": answer,
            "phone": "+65 6123 4567",
            "email": "support@acme.com",
        }
    }
    path = tmp_path / "brands.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(ev, "GROUND_TRUTH_FILE", path)

    name_result = ev.validate_name(answer, data["Acme"])
    email_result = ev.validate_email(answer, data["Acme"])
    address_result = ev.validate_address(answer, data["Acme"])

    assert name_result["passed"] is True
    assert email_result["passed"] is True
    assert address_result["passed"] is True

    overall = ev.nape_consistency_score(answer, "Acme")
    assert overall["passed"] is True
