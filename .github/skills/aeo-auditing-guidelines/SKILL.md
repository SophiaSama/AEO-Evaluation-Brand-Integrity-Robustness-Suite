---
name: aeo_auditing-guidelines
description: This skill enables an AI Agent to evaluate the "AI-Readiness" and "Fact-Authenticity" of a brand’s digital footprint across Answer Engines (Gemini, Perplexity, GPT-Search).
---

## Core Competencies
 - Semantic Consistency: Detecting "Sentiment Drift" between different LLM responses.

 - Source Provenance: Verifying if an AI citation originates from an Authorized Source.

 - Schema Validation: Ensuring JSON-LD metadata aligns with the "Ground Truth."

## The AEO Audit Guidelines (The "General Rules")
When auditing an AEO environment, follow these four mandatory testing pillars:

### Rule 1: The Authority Handshake (Provenance)
Requirement: Every fact cited by the LLM must be traceable to a source with a C2PA (Content Credentials) manifest or a verified Entity ID.

Test Case: If an LLM cites an anonymous forum post over an official .com.sg site, mark as a Priority 1: Authority Failure.

### Rule 2: NAP+E Consistency (The "Fact" Check)
Requirement: Ensure Name, Address, Phone, and Entity details are identical across the Brand Site, Knowledge Graphs, and LLM summaries.

Test Case: Inject a query asking for the "Headquarters of [Brand]." If the AI returns a "poisoned" address from a fake directory, the system fails the Entity Integrity test.

### Rule 3: The "Direct Answer" Latency
Requirement: The brand’s primary value proposition must be extractable by the AI in the first 150 tokens of the landing page.

Test Case: Use a Python scraper to check if the "Direct Answer" (e.g., "What does this product do?") is buried behind a marketing wall or javascript.

### Rule 4: Adversarial Resilience (Data Poisoning)
Requirement: The AI must ignore high-volume "noise" (e.g., 50 fake bad reviews) if the "Official Truth" is digitally signed.

Test Case: Simulate 10 "poisoned" snippets in a Sandbox RAG. If the Auditor Agent adopts the lies, the Bidding AI is compromised.

## Technical Verification Checklist
| Technical Layer | Audit Action | Verification Tool
|---|---|---|
|Metadata|Verify FAQPage and Product Schema|Google Rich Results Test
|Provenance|Check for C2PA digital signatures|C2PA Verify Tool
|Network|Validate SSL/TLS and DNS entries|dig / nslookup (Python subprocess)
|Consistency|Run Cosine Similarity on LLM outputs|Scikit-learn (Python)

## Project Lessons Learned
- Search provider change: DuckDuckGo search renamed to `ddgs`. Use a fallback import to avoid runtime warnings.
- Extraction robustness: trafilatura can return empty text for some pages; add an HTML text fallback to avoid zero-document crawls.

## Singapore Compliance (IMDA 2026)
This skill aligns with the Singapore Model AI Governance Framework (v2026):

 - Explainability: Every audit score must include a link to the specific citation that caused the failure.

 - Human-in-the-Loop: High-risk discrepancies (e.g., fake security warnings) must trigger an immediate alert to the human QA Lead.

## Agent "Tools" for this Skill
To build this in Python, your agent should have access to these functions:

 - get_llm_citation_path(url): Traces the source of an AI claim.

 ```python
 from sentence_transformers import CrossEncoder

@tool
def get_llm_citation_path(url: str, claim: str) -> dict:
    """Verifies if the 'claim' is actually present in the 'url' provided."""
    content = fetch_page_text(url) # Your scraping logic
    model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    score = model.predict([claim, content])

    return {
        "source": url,
        "veracity_score": float(score), # High score = Truthful citation
        "status": "PASS" if score > 0.5 else "FAIL: Hallucinated Citation"
    }
 ```

 - validate_schema_integrity(html_content): Checks for logic errors in JSON-LD.
 ```python
 import extruct
from jsonschema import validate

@tool
def validate_schema_integrity(html_content: str) -> bool:
    """Checks if the hidden JSON-LD metadata follows the correct brand schema."""
    data = extruct.extract(html_content, syntaxes=['json-ld'])

    # Define your 'Strict' Brand Schema (e.g., must have 'Price' and 'Currency')
    brand_schema = {
        "type": "object",
        "properties": {"price": {"type": "string"}, "currency": {"type": "string"}},
        "required": ["price", "currency"]
    }

    try:
        validate(instance=data['json-ld'][0], schema=brand_schema)
        return True
    except Exception as e:
        return f"Schema Integrity Error: {e}"
 ```

 - calculate_sentiment_drift(query): Compares responses from Gemini vs. Llama 3.
 ```python
 from textblob import TextBlob
import numpy as np

@tool
def calculate_sentiment_drift(query: str) -> dict:
    """Compares how different AI models 'feel' about a brand query."""
    responses = [call_gemini(query), call_gpt4(query), call_llama3(query)]
    scores = [TextBlob(r).sentiment.polarity for r in responses]

    drift = np.std(scores) # High standard deviation = Conflicting AI opinions
    return {"drift_score": drift, "risk_level": "HIGH" if drift > 0.4 else "STABLE"}
 ```

## Example - Python Script: NAP+E Consistency Auditor

This script uses BeautifulSoup for extraction and SequenceMatcher for fuzzy logic (essential because AI often formats addresses differently than a database).

```python

import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import re

# 1. THE ORACLE (Your Ground Truth)
# This would typically come from an ACRA filing or an internal DB
GROUND_TRUTH = {
    "brand_name": "EcoMum Singapore",
    "address": "10 Anson Road, #10-11 International Plaza, Singapore 079903",
    "phone": "+65 6123 4567",
    "entity_type": "Private Limited Company"
}

def fuzzy_match(a, b):
    """Returns a ratio of similarity (0 to 1). Addresses often have minor string diffs."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def audit_website(url):
    print(f"--- Starting AEO Audit for: {url} ---")
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        # 2. EXTRACTION LOGIC (The "Actual" Data)
        # In a real agent, you'd use an LLM to extract these, 
        # but here we'll use regex for a deterministic 'System Test' approach.
        extracted_phone = re.search(r'(\+65\s?\d{4}\s?\d{4})', page_text)
        
        # 3. ASSERTIONS
        results = []
        
        # Test Name
        name_score = fuzzy_match(GROUND_TRUTH["brand_name"], soup.title.string if soup.title else "")
        results.append(("Name Match", "PASS" if name_score > 0.8 else "FAIL", f"Score: {name_score:.2f}"))

        # Test Phone
        actual_phone = extracted_phone.group(0) if extracted_phone else "NOT FOUND"
        phone_match = (actual_phone == GROUND_TRUTH["phone"])
        results.append(("Phone Match", "PASS" if phone_match else "FAIL", f"Found: {actual_phone}"))

        # Test Address (Look for keywords in the page text)
        address_found = GROUND_TRUTH["address"].split(",")[0] in page_text # Checks '10 Anson Road'
        results.append(("Address Anchor", "PASS" if address_found else "FAIL", "Anchor text not found"))

        # 4. REPORTING
        print(f"{'TEST CASE':<20} | {'STATUS':<10} | {'DETAILS'}")
        print("-" * 60)
        for test, status, detail in results:
            print(f"{test:<20} | {status:<10} | {detail}")

    except Exception as e:
        print(f"Audit failed due to system error: {e}")

# Simulate auditing a 'hatching' brand's temporary landing page
# audit_website("https://example-brand-site.sg")
```