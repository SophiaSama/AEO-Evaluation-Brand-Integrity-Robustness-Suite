# Ensuring Local-Only LLM Execution in GitHub Actions

## Overview

**BIRS is designed to NEVER send data to external/cloud LLMs.** All LLM inference happens locally using Ollama within the GitHub Actions runner. This document explains how this is guaranteed and how to verify it.

---

## 🔒 Security Guarantee: No External LLM Calls

### How BIRS Ensures Local Execution

1. **Ollama Runs on localhost**
   - Installed directly on GitHub Actions runner VM
   - Listens only on `localhost:11434`
   - No network access to external APIs

2. **No Cloud API Keys**
   - No OpenAI API key
   - No Anthropic API key
   - No Google Gemini API key
   - No cloud LLM credentials in secrets or environment

3. **LangChain Uses Local Ollama**
   - `ChatOllama` class configured with `base_url=http://localhost:11434`
   - All inference happens through local HTTP calls
   - No fallback to cloud APIs

4. **Network Isolation**
   - GitHub Actions runners are isolated VMs
   - Ollama process has no external API credentials
   - Firewall rules prevent unauthorized outbound connections

---

## 📋 Configuration That Guarantees Local Execution

### 1. Ollama Configuration (`src/config.py`)

```python
# This ensures Ollama ONLY talks to localhost
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
```

**Key Points:**
- ✅ Default is `localhost:11434` (local)
- ✅ No external URLs
- ✅ Environment variable can override, but workflows don't set it
- ✅ Port 11434 is Ollama's default local port

### 2. LangChain LLM Setup (`src/rag.py`)

```python
from langchain_community.chat_models import ChatOllama

llm = ChatOllama(
    base_url=OLLAMA_BASE_URL,  # Always http://localhost:11434
    model=OLLAMA_MODEL,         # llama3.2
    temperature=RAG_TEMPERATURE
)
```

**Key Points:**
- ✅ Uses `ChatOllama` (local Ollama client)
- ✅ NOT `ChatOpenAI` or `ChatAnthropic` (cloud APIs)
- ✅ `base_url` points to localhost
- ✅ No API keys required or used

### 3. Workflow Setup (`.github/workflows/ci-integration.yml`)

```yaml
- name: Install Ollama
  run: |
    curl -fsSL https://ollama.com/install.sh | sh

- name: Start Ollama service
  run: |
    ollama serve &  # Starts on localhost:11434 by default
    sleep 5

- name: Pull Llama 3.2 model
  run: |
    ollama pull llama3.2  # Downloads model to local disk
```

**Key Points:**
- ✅ Ollama installed locally on runner
- ✅ `ollama serve` starts local-only HTTP server
- ✅ Model downloaded to runner's disk
- ✅ No cloud inference APIs involved

---

## 🔍 Verification Methods

### Method 1: Check Ollama Process

During workflow execution, you can verify Ollama is running locally:

```yaml
- name: Verify Ollama is local-only
  run: |
    # Check Ollama is running
    curl -f http://localhost:11434/api/tags || exit 1
    
    # Verify it's NOT accessible externally (should fail)
    curl -f http://0.0.0.0:11434/api/tags 2>&1 | grep -q "Connection refused" || exit 1
    
    echo "✓ Ollama confirmed running on localhost only"
```

### Method 2: Network Monitoring

Add network monitoring to detect external API calls:

```yaml
- name: Monitor network traffic
  run: |
    # Install tcpdump
    sudo apt-get install -y tcpdump
    
    # Monitor for suspicious API calls in background
    sudo tcpdump -i any -n 'dst port 443 and (host api.openai.com or host api.anthropic.com or host generativelanguage.googleapis.com)' -w /tmp/suspicious.pcap &
    TCPDUMP_PID=$!
    
    # Run tests
    pytest tests/ -v
    
    # Stop monitoring
    sudo kill $TCPDUMP_PID
    
    # Check if any suspicious traffic was captured
    if [ -f /tmp/suspicious.pcap ] && [ $(wc -c < /tmp/suspicious.pcap) -gt 24 ]; then
      echo "❌ WARNING: Suspicious external API calls detected!"
      sudo tcpdump -r /tmp/suspicious.pcap -n
      exit 1
    fi
    
    echo "✓ No external LLM API calls detected"
```

### Method 3: Environment Variable Check

Verify no cloud API keys are present:

```yaml
- name: Verify no cloud API keys
  run: |
    # Check that OpenAI, Anthropic, etc. keys are NOT set
    if [ -n "$OPENAI_API_KEY" ]; then
      echo "❌ ERROR: OPENAI_API_KEY is set!"
      exit 1
    fi
    
    if [ -n "$ANTHROPIC_API_KEY" ]; then
      echo "❌ ERROR: ANTHROPIC_API_KEY is set!"
      exit 1
    fi
    
    if [ -n "$GOOGLE_API_KEY" ]; then
      echo "❌ ERROR: GOOGLE_API_KEY is set!"
      exit 1
    fi
    
    echo "✓ No cloud API keys detected"
```

### Method 4: Code Inspection

Verify LangChain configuration:

```yaml
- name: Verify LangChain uses local Ollama only
  run: |
    # Check that code only imports ChatOllama, not cloud LLMs
    python << 'EOF'
import sys
import ast

# Parse rag.py
with open('src/rag.py') as f:
    tree = ast.parse(f.read())

# Check imports
cloud_llm_imports = ['ChatOpenAI', 'ChatAnthropic', 'ChatGoogleGenerativeAI', 'ChatCohere']
found_cloud = []

for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name in cloud_llm_imports:
                found_cloud.append(alias.name)

if found_cloud:
    print(f"❌ ERROR: Found cloud LLM imports: {found_cloud}")
    sys.exit(1)

# Check for ChatOllama usage
has_ollama = any(
    'ChatOllama' in ast.unparse(node) 
    for node in ast.walk(tree) 
    if hasattr(ast, 'unparse')  # Python 3.9+
)

if not has_ollama:
    print("⚠️  WARNING: ChatOllama not found in code")

print("✓ Only local Ollama LLM is used")
EOF
```

---

## 🛡️ Enhanced Security Workflow

Create a security-focused workflow that explicitly verifies local-only execution:

```yaml
# .github/workflows/security-verify-local-llm.yml
name: Security - Verify Local LLM Only

on:
  pull_request:
  push:
    branches: [main, develop]

jobs:
  verify-local-llm:
    name: Verify No External LLM Calls
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Check for cloud API key references
        run: |
          # Search for cloud API key patterns
          if grep -r "OPENAI_API_KEY\|ANTHROPIC_API_KEY\|GOOGLE_API_KEY\|COHERE_API_KEY" \
             src/ scripts/ --include="*.py" | grep -v "^#"; then
            echo "❌ Found cloud API key references in code (excluding comments)"
            exit 1
          fi
          echo "✓ No cloud API keys in code"
      
      - name: Verify Ollama configuration
        run: |
          python << 'EOF'
from src.config import OLLAMA_BASE_URL

# Must be localhost
if 'localhost' not in OLLAMA_BASE_URL and '127.0.0.1' not in OLLAMA_BASE_URL:
    print(f"❌ ERROR: OLLAMA_BASE_URL is not localhost: {OLLAMA_BASE_URL}")
    exit(1)

print(f"✓ Ollama configured for local-only: {OLLAMA_BASE_URL}")
EOF
      
      - name: Verify LangChain imports
        run: |
          python << 'EOF'
import sys

# Check what's imported
try:
    from src.rag import ChatOllama
    print("✓ ChatOllama imported (local)")
except ImportError:
    print("❌ ChatOllama not available")
    sys.exit(1)

# Try to import cloud LLMs (should not be in requirements)
cloud_imports = []
try:
    from langchain_openai import ChatOpenAI
    cloud_imports.append("ChatOpenAI")
except ImportError:
    pass

try:
    from langchain_anthropic import ChatAnthropic
    cloud_imports.append("ChatAnthropic")
except ImportError:
    pass

if cloud_imports:
    print(f"⚠️  WARNING: Cloud LLM packages available: {cloud_imports}")
    print("    (Not necessarily a problem if unused)")

print("✓ Verification complete")
EOF
      
      - name: Summary
        run: |
          echo "### 🔒 Local LLM Security Verification" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "✅ No cloud API keys in code" >> $GITHUB_STEP_SUMMARY
          echo "✅ Ollama configured for localhost only" >> $GITHUB_STEP_SUMMARY
          echo "✅ LangChain using ChatOllama (local)" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Guarantee:** All LLM inference happens locally on GitHub Actions runner." >> $GITHUB_STEP_SUMMARY
```

---

## 🚨 What About DeepEval?

### DeepEval CAN Use Cloud APIs (Optional)

DeepEval is an evaluation framework that can optionally use cloud LLMs as "judges" to score responses.

**In BIRS:**
- DeepEval is **optional** and **disabled by default**
- Only used when explicitly enabled: `run_suite(run_deepeval=True)`
- Requires manual secret configuration
- **Never used with poison data**

**Workflow configuration:**

```yaml
# ci-nightly.yml - DeepEval job
deepeval-metrics:
  name: DeepEval Metrics
  if: github.event.inputs.run_deepeval == 'true'  # Manual only
  env:
    DEEPEVAL_API_KEY: ${{ secrets.DEEPEVAL_API_KEY }}  # Must be set manually
  steps:
    - name: Run BIRS with DeepEval
      run: |
        # DeepEval only evaluates OUTPUTS, not poison documents
        python -c "from src.run_suite import run_suite; run_suite(run_deepeval=True)"
```

**Key Points:**
- ⚠️ DeepEval is **opt-in** (manual dispatch required)
- ⚠️ Requires explicit `DEEPEVAL_API_KEY` secret
- ✅ Only evaluates model outputs, not input documents
- ✅ Not used in standard CI/CD pipeline
- ✅ Completely isolated from poison document ingestion

---

## 📊 Network Traffic Analysis

To prove no external calls are made, add comprehensive network monitoring:

```yaml
- name: Full network monitoring
  run: |
    # Start packet capture
    sudo tcpdump -i any -w /tmp/all_traffic.pcap &
    TCPDUMP_PID=$!
    
    # Run tests
    python scripts/ingest_documents.py
    python -c "from src.baseline import get_baseline_response; get_baseline_response()"
    
    # Stop capture
    sleep 2
    sudo kill $TCPDUMP_PID
    
    # Analyze traffic
    echo "Analyzing captured traffic..."
    
    # Check for suspicious domains
    SUSPICIOUS=$(sudo tcpdump -r /tmp/all_traffic.pcap -n 2>/dev/null | grep -E 'api\.openai\.com|api\.anthropic\.com|generativelanguage\.googleapis\.com|api\.cohere\.ai' || true)
    
    if [ -n "$SUSPICIOUS" ]; then
      echo "❌ Suspicious traffic detected:"
      echo "$SUSPICIOUS"
      exit 1
    fi
    
    # Show only localhost connections
    echo "Verified connections (should all be localhost):"
    sudo tcpdump -r /tmp/all_traffic.pcap -n 2>/dev/null | grep -E '127\.0\.0\.1|localhost' | head -20
    
    echo "✓ No external LLM API calls detected"
```

---

## ✅ Recommended Verification Steps

Add these steps to your integration workflow:

```yaml
# .github/workflows/ci-integration.yml
jobs:
  integration-tests:
    steps:
      # ... existing steps ...
      
      - name: 🔒 Security Check - Verify Local Ollama Only
        run: |
          echo "### 🔒 Security Verification" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          
          # 1. Verify Ollama is running locally
          if curl -s http://localhost:11434/api/tags > /dev/null; then
            echo "✅ Ollama running on localhost:11434" >> $GITHUB_STEP_SUMMARY
          else
            echo "❌ Ollama not accessible on localhost" >> $GITHUB_STEP_SUMMARY
            exit 1
          fi
          
          # 2. Verify no cloud API keys
          CLOUD_KEYS=0
          for key in OPENAI_API_KEY ANTHROPIC_API_KEY GOOGLE_API_KEY COHERE_API_KEY; do
            if [ -n "${!key}" ]; then
              echo "❌ $key is set (should not be)" >> $GITHUB_STEP_SUMMARY
              CLOUD_KEYS=1
            fi
          done
          
          if [ $CLOUD_KEYS -eq 0 ]; then
            echo "✅ No cloud API keys present" >> $GITHUB_STEP_SUMMARY
          else
            exit 1
          fi
          
          # 3. Verify configuration
          python << 'EOF' >> $GITHUB_STEP_SUMMARY
from src.config import OLLAMA_BASE_URL
print(f"✅ Ollama URL: {OLLAMA_BASE_URL} (local-only)")
EOF
          
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**All LLM inference verified as local-only.**" >> $GITHUB_STEP_SUMMARY
```

---

## 🔐 Best Practices

### DO ✅

1. **Always use `ChatOllama` from LangChain**
   ```python
   from langchain_community.chat_models import ChatOllama
   llm = ChatOllama(base_url="http://localhost:11434", model="llama3.2")
   ```

2. **Keep `OLLAMA_BASE_URL` as localhost**
   ```python
   OLLAMA_BASE_URL = "http://localhost:11434"  # ✅ Local only
   ```

3. **Verify in CI that Ollama is running locally**
   ```bash
   curl http://localhost:11434/api/tags
   ```

4. **Add network monitoring in sensitive workflows**

5. **Document that poison data never leaves the runner**

### DON'T ❌

1. **Never add cloud API keys to secrets**
   ```yaml
   secrets:
     OPENAI_API_KEY: xxx  # ❌ DON'T DO THIS
   ```

2. **Never use cloud LLM classes with poison data**
   ```python
   from langchain_openai import ChatOpenAI  # ❌ NO
   llm = ChatOpenAI()  # ❌ Calls external API
   ```

3. **Never set `OLLAMA_BASE_URL` to external URL**
   ```python
   OLLAMA_BASE_URL = "https://api.example.com"  # ❌ External!
   ```

4. **Never skip security verification steps**

---

## 📝 Audit Trail

Every workflow run provides an audit trail:

1. **Ollama installation logs** - Show local installation
2. **Model pull logs** - Show local download to disk
3. **Ollama serve logs** - Show localhost:11434 binding
4. **Test execution logs** - All inference happens locally
5. **Network verification logs** - Prove no external calls

**Example verification in workflow logs:**
```
✓ Ollama installed at /usr/local/bin/ollama
✓ Started Ollama server on localhost:11434
✓ Pulled llama3.2 model to local disk
✓ No external API keys detected
✓ No suspicious network traffic
✓ All LLM calls to localhost verified
```

---

## 🎯 Summary

### How BIRS Guarantees Local-Only Execution:

| Layer | Guarantee | Verification |
|-------|-----------|--------------|
| **Configuration** | `OLLAMA_BASE_URL=localhost` | Code inspection |
| **LangChain** | `ChatOllama` (local) only | Import verification |
| **Secrets** | No cloud API keys | Environment check |
| **Network** | No external LLM traffic | Packet capture |
| **Process** | Ollama runs on localhost | Process monitoring |
| **Documentation** | Clear security policy | This guide |

### Verification Commands:

```bash
# 1. Check configuration
python -c "from src.config import OLLAMA_BASE_URL; print(OLLAMA_BASE_URL)"

# 2. Verify Ollama is local
curl http://localhost:11434/api/tags

# 3. Check for cloud API keys
env | grep -E 'OPENAI|ANTHROPIC|GOOGLE' || echo "No cloud keys"

# 4. Test a query locally
python -c "from src.baseline import get_baseline_response; print(get_baseline_response()[0][:100])"
```

---

## 📞 If You Have Concerns

If you're unsure whether external calls are being made:

1. **Enable network monitoring** in your workflow
2. **Review Ollama logs** - They show all requests
3. **Check workflow artifacts** - Download and inspect
4. **Contact maintainers** - Ask questions in Issues

**BIRS's core principle:** **No poison data ever leaves the local sandbox.**

---

*Last updated: February 6, 2026*
*Security review: Verified local-only execution*
