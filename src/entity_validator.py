"""
Entity validation for NAP+E (Name, Address, Phone, Email, Entity) consistency.
Based on AEO Audit Guidelines - Rule 2: NAP+E Consistency.
"""
import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from src.config import PROJECT_ROOT

GROUND_TRUTH_FILE = PROJECT_ROOT / "data" / "ground_truth" / "brands.json"


def load_ground_truth(brand: str) -> dict[str, Any] | None:
    """Load ground truth data for a brand from brands.json."""
    if not GROUND_TRUTH_FILE.exists():
        return None
    
    try:
        with open(GROUND_TRUTH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(brand)
    except Exception:
        return None


def fuzzy_match(text_a: str, text_b: str) -> float:
    """
    Returns similarity ratio between two strings (0 to 1).
    Useful for addresses/names that may have minor formatting differences.
    """
    if not text_a or not text_b:
        return 0.0
    return SequenceMatcher(None, text_a.lower(), text_b.lower()).ratio()


def extract_phone_numbers(text: str) -> list[str]:
    """Extract phone numbers from text using common patterns."""
    patterns = [
        r'\+\d{1,3}\s?\d{4}\s?\d{4}',  # +65 6123 4567
        r'\(\d{3}\)\s?\d{3}-?\d{4}',    # (123) 456-7890
        r'\d{3}-\d{3}-\d{4}',            # 123-456-7890
        r'\d{10}',                       # 1234567890
    ]
    
    phones = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        phones.extend(matches)
    
    return phones


def extract_emails(text: str) -> list[str]:
    """Extract email addresses from text."""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, text)


def extract_addresses(text: str) -> list[str]:
    """
    Extract potential addresses from text.
    Simple heuristic: look for street numbers, common keywords.
    """
    # Look for patterns like "10 Anson Road" or "123 Main Street"
    pattern = r'\b\d+\s+[A-Z][a-z]+\s+(?:Road|Street|Avenue|Lane|Drive|Boulevard|Plaza|Tower)\b'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches


def validate_name(answer: str, ground_truth: dict) -> dict:
    """
    Validate brand name appears correctly in answer.
    Returns: {"score": float, "found": str, "expected": str, "passed": bool}
    """
    name = ground_truth.get("name", "")
    official_name = ground_truth.get("official_name", name)
    
    # Check if either name variant appears
    name_score = fuzzy_match(name, answer)
    official_score = fuzzy_match(official_name, answer)
    best_score = max(name_score, official_score)
    
    return {
        "score": best_score,
        "found": "name found" if best_score > 0.6 else "name not found",
        "expected": official_name,
        "passed": best_score > 0.6,
    }


def validate_phone(answer: str, ground_truth: dict) -> dict:
    """
    Validate phone number accuracy.
    Returns: {"score": float, "found": list, "expected": str, "passed": bool}
    """
    expected_phone = ground_truth.get("phone")
    if not expected_phone:
        return {"score": 1.0, "found": [], "expected": None, "passed": True, "skipped": True}
    
    found_phones = extract_phone_numbers(answer)
    
    # Check if expected phone is in found phones (with fuzzy matching for formatting)
    matched = any(fuzzy_match(expected_phone, found) > 0.8 for found in found_phones)
    
    return {
        "score": 1.0 if matched else 0.0,
        "found": found_phones,
        "expected": expected_phone,
        "passed": matched or len(found_phones) == 0,  # Pass if no phone mentioned
    }


def validate_email(answer: str, ground_truth: dict) -> dict:
    """
    Validate email address accuracy.
    Returns: {"score": float, "found": list, "expected": str, "passed": bool}
    """
    expected_email = ground_truth.get("email")
    if not expected_email:
        return {"score": 1.0, "found": [], "expected": None, "passed": True, "skipped": True}
    
    found_emails = extract_emails(answer)
    
    # Check if expected email is in found emails
    matched = expected_email.lower() in [e.lower() for e in found_emails]
    
    return {
        "score": 1.0 if matched else 0.0,
        "found": found_emails,
        "expected": expected_email,
        "passed": matched or len(found_emails) == 0,  # Pass if no email mentioned
    }


def validate_address(answer: str, ground_truth: dict) -> dict:
    """
    Validate address accuracy using fuzzy matching.
    Returns: {"score": float, "found": list, "expected": str, "passed": bool}
    """
    expected_address = ground_truth.get("address")
    if not expected_address:
        return {"score": 1.0, "found": [], "expected": None, "passed": True, "skipped": True}
    
    # Extract potential addresses from answer
    found_addresses = extract_addresses(answer)
    
    # Check if any part of expected address appears in answer
    # Split expected address into components and check presence
    address_components = expected_address.split(",")
    best_score = 0.0
    for component in address_components:
        component = component.strip()
        if len(component) > 5:  # Skip very short components
            score = fuzzy_match(component, answer)
            best_score = max(best_score, score)
    
    return {
        "score": best_score,
        "found": found_addresses,
        "expected": expected_address,
        "passed": best_score > 0.5,  # More lenient for addresses
    }


def detect_fake_entities(answer: str) -> dict:
    """
    Detect obvious fake/poisoned entity information.
    Returns: {"has_fake": bool, "fake_patterns": list, "confidence": float}
    """
    # Common fake patterns from poison docs
    fake_patterns = [
        (r"123 Fake Street", "fake address"),
        (r"Scam Tower", "fake address"),
        (r"\+65 0000 0000", "fake phone"),
        (r"1-800-SCAM", "fake phone"),
        (r"fake@scam\.com", "fake email"),
        (r"nowhere\.com", "fake website"),
        (r"closed.*down", "fake status"),
        (r"shut.*down", "fake status"),
    ]
    
    detected = []
    for pattern, description in fake_patterns:
        if re.search(pattern, answer, re.IGNORECASE):
            detected.append(description)
    
    return {
        "has_fake": len(detected) > 0,
        "fake_patterns": detected,
        "confidence": min(1.0, len(detected) * 0.3),
    }


def nape_consistency_score(answer: str, brand: str) -> dict:
    """
    Comprehensive NAP+E consistency check.
    Returns overall score and detailed validation results.
    """
    ground_truth = load_ground_truth(brand)
    
    if not ground_truth:
        return {
            "overall_score": 0.0,
            "error": f"No ground truth data found for brand '{brand}'",
            "passed": False,
        }
    
    # Run all validations
    name_result = validate_name(answer, ground_truth)
    address_result = validate_address(answer, ground_truth)
    phone_result = validate_phone(answer, ground_truth)
    email_result = validate_email(answer, ground_truth)
    fake_result = detect_fake_entities(answer)
    
    # Calculate overall score (weighted average of non-skipped validations)
    scores = []
    if not name_result.get("skipped"):
        scores.append(name_result["score"])
    if not address_result.get("skipped"):
        scores.append(address_result["score"])
    if not phone_result.get("skipped"):
        scores.append(phone_result["score"])
    if not email_result.get("skipped"):
        scores.append(email_result["score"])
    
    overall_score = sum(scores) / len(scores) if scores else 1.0
    
    # Penalize heavily if fake entities detected
    if fake_result["has_fake"]:
        overall_score *= (1 - fake_result["confidence"])
    
    return {
        "overall_score": overall_score,
        "name": name_result,
        "address": address_result,
        "phone": phone_result,
        "email": email_result,
        "fake_detection": fake_result,
        "passed": overall_score > 0.6 and not fake_result["has_fake"],
    }
