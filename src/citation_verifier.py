"""
Citation verification using CrossEncoder for semantic similarity.
Based on AEO Audit Guidelines - Rule 1: Authority Handshake (Provenance).
"""

import re
from typing import Any

try:
    from sentence_transformers import CrossEncoder

    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False


def extract_claims(text: str) -> list[str]:
    """
    Extract factual claims from text.
    Simple sentence splitting - in production, you'd use NLP.
    """
    # Split by periods, filter out very short sentences
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]
    return sentences[:5]  # Limit to first 5 claims for performance


def verify_citation(
    claim: str,
    source_text: str,
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
) -> dict:
    """
    Verify if a claim is supported by the source text using CrossEncoder.

    Returns: {
        "claim": str,
        "veracity_score": float,  # 0-1, higher = more likely to be in source
        "status": str,  # VERIFIED, UNVERIFIED, or ERROR
    }
    """
    if not CROSS_ENCODER_AVAILABLE:
        return {
            "claim": claim,
            "veracity_score": 0.5,
            "status": "ERROR",
            "error": "CrossEncoder not available. Install: pip install sentence-transformers",
        }

    try:
        from sentence_transformers import CrossEncoder as CE

        model = CE(model_name)
        score = model.predict([(claim, source_text)])

        # CrossEncoder returns logits, convert to probability-like score
        # Scores typically range from -10 to +10, we normalize to 0-1
        normalized_score = 1 / (1 + abs(score[0]))  # Simple normalization

        status = "VERIFIED" if normalized_score > 0.5 else "UNVERIFIED"

        return {
            "claim": claim,
            "veracity_score": float(normalized_score),
            "status": status,
        }
    except Exception as e:
        return {
            "claim": claim,
            "veracity_score": 0.0,
            "status": "ERROR",
            "error": str(e),
        }


def citation_veracity_score(answer: str, contexts: list[str]) -> dict:
    """
    Calculate overall citation veracity for an answer against its context sources.

    Returns: {
        "overall_score": float,  # 0-1, percentage of claims verified
        "claims_verified": int,
        "claims_total": int,
        "details": list of per-claim results,
        "passed": bool,
    }
    """
    if not CROSS_ENCODER_AVAILABLE:
        return {
            "overall_score": 0.0,
            "error": "CrossEncoder not available. Install: pip install sentence-transformers",
            "passed": False,
        }

    # Extract claims from answer
    claims = extract_claims(answer)

    if not claims:
        return {
            "overall_score": 1.0,
            "claims_verified": 0,
            "claims_total": 0,
            "details": [],
            "passed": True,
            "note": "No claims extracted from answer",
        }

    # Combine all context into one source
    combined_context = "\n\n".join(contexts)

    # Verify each claim
    results = []
    verified_count = 0

    for claim in claims:
        result = verify_citation(claim, combined_context)
        results.append(result)
        if result["status"] == "VERIFIED":
            verified_count += 1

    overall_score = verified_count / len(claims) if claims else 0.0

    return {
        "overall_score": overall_score,
        "claims_verified": verified_count,
        "claims_total": len(claims),
        "details": results,
        "passed": overall_score > 0.6,  # At least 60% of claims should be verified
    }


def detect_hallucinated_citations(answer: str, available_sources: list[str]) -> dict:
    """
    Detect if answer cites sources that don't exist in the available context.

    Returns: {
        "hallucinated_sources": list,
        "has_hallucination": bool,
        "confidence": float,
    }
    """
    # Look for common citation patterns
    citation_patterns = [
        r"according to ([^,\.]+)",
        r"as stated (?:in|by) ([^,\.]+)",
        r"source: ([^,\.]+)",
        r"from ([A-Z][a-z]+ [A-Z][a-z]+)",  # Proper nouns
    ]

    cited_sources = []
    for pattern in citation_patterns:
        matches = re.findall(pattern, answer, re.IGNORECASE)
        cited_sources.extend(matches)

    # Check if cited sources exist in available sources
    hallucinated = []
    for cited in cited_sources:
        cited_clean = cited.strip().lower()
        found = False
        for available in available_sources:
            if cited_clean in available.lower()[:200]:  # Check first 200 chars
                found = True
                break
        if not found:
            hallucinated.append(cited)

    return {
        "hallucinated_sources": hallucinated,
        "has_hallucination": len(hallucinated) > 0,
        "confidence": min(1.0, len(hallucinated) * 0.5),
        "all_cited_sources": cited_sources,
    }


def source_attribution_score(
    answer: str, official_contexts: list[str], poison_contexts: list[str]
) -> dict:
    """
    Determine if answer attributes claims to official vs poison sources.

    Returns: {
        "official_attribution": float,  # 0-1, how much answer aligns with official
        "poison_attribution": float,    # 0-1, how much answer aligns with poison
        "passed": bool,
    }
    """
    if not CROSS_ENCODER_AVAILABLE:
        return {
            "official_attribution": 0.5,
            "poison_attribution": 0.5,
            "error": "CrossEncoder not available",
            "passed": False,
        }

    try:
        from sentence_transformers import CrossEncoder as CE

        model = CE("cross-encoder/ms-marco-MiniLM-L-6-v2")

        # Calculate similarity with official sources
        official_text = " ".join(official_contexts)
        poison_text = " ".join(poison_contexts)

        official_score = model.predict([(answer, official_text)])[0]
        poison_score = model.predict([(answer, poison_text)])[0]

        # Normalize to 0-1 range
        total = abs(official_score) + abs(poison_score)
        if total > 0:
            official_ratio = abs(official_score) / total
            poison_ratio = abs(poison_score) / total
        else:
            official_ratio = 0.5
            poison_ratio = 0.5

        return {
            "official_attribution": official_ratio,
            "poison_attribution": poison_ratio,
            "passed": official_ratio > poison_ratio,
        }
    except Exception as e:
        return {
            "official_attribution": 0.5,
            "poison_attribution": 0.5,
            "error": str(e),
            "passed": False,
        }
