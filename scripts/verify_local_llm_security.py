#!/usr/bin/env python3
"""Verify local-only LLM settings for CI.

Prints human-readable status lines suitable for appending to $GITHUB_STEP_SUMMARY.
Exits non-zero on failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path to allow importing from src
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL  # noqa: E402


def main() -> None:
    if "localhost" in OLLAMA_BASE_URL or "127.0.0.1" in OLLAMA_BASE_URL:
        print(f"✅ Ollama URL: {OLLAMA_BASE_URL} (local-only)")
    else:
        print(f"❌ ERROR: Ollama URL is not localhost: {OLLAMA_BASE_URL}")
        raise SystemExit(1)

    print(f"✅ Ollama model: {OLLAMA_MODEL}")

    try:
        # Ensures we use the local ChatOllama integration.
        from src.rag import ChatOllama  # noqa: F401

        print("✅ LangChain using ChatOllama (local)")
    except ImportError as e:
        print(f"❌ ERROR: Cannot import ChatOllama: {e}")
        raise SystemExit(1)

    # Basic static check that we aren't referencing cloud chat model classes.
    with open("src/rag.py", encoding="utf-8") as f:
        content = f.read()

    cloud_llms = ["ChatOpenAI", "ChatAnthropic", "ChatGoogleGenerativeAI"]
    for llm in cloud_llms:
        if llm in content:
            print(f"⚠️  WARNING: Found {llm} referenced in rag.py")

    print("✅ No blocking cloud LLM imports detected")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise
    finally:
        sys.stdout.flush()
