# Testing BIRS with Different Models

## Overview

BIRS supports testing with **any Ollama-compatible model**. You can easily switch between models using environment variables, command-line arguments, or configuration files.

---

## 🎯 Quick Start

### Method 1: Environment Variable (Easiest)

```bash
# Test with a different model
export OLLAMA_MODEL=mistral
python -m src.run_suite

# Or inline
OLLAMA_MODEL=phi3 python -m src.run_suite
```

### Method 2: `.env` File (Recommended for Development)

```bash
# Copy example and edit
cp .env.example .env

# Edit .env
OLLAMA_MODEL=mistral
```

Then run normally:
```bash
python -m src.run_suite
```

### Method 3: Python Code

```python
import os
os.environ['OLLAMA_MODEL'] = 'mistral'

from src.run_suite import run_suite
run_suite()
```

---

## 📋 Supported Models

### Ollama Model Library

Any model from [Ollama Library](https://ollama.com/library) works. Popular choices:

| Model | Size | Best For | Speed | Quality |
|-------|------|----------|-------|---------|
| **llama3.2** | 2GB | General, fast | ⚡⚡⚡ | ⭐⭐⭐ |
| **llama3.1:8b** | 4.7GB | Balanced | ⚡⚡ | ⭐⭐⭐⭐ |
| **mistral** | 4.1GB | Instruction following | ⚡⚡ | ⭐⭐⭐⭐ |
| **phi3** | 2.3GB | Small, efficient | ⚡⚡⚡ | ⭐⭐⭐ |
| **gemma2:2b** | 1.6GB | Very fast | ⚡⚡⚡⚡ | ⭐⭐ |
| **qwen2.5:7b** | 4.7GB | Multilingual | ⚡⚡ | ⭐⭐⭐⭐ |
| **llama3.1:70b** | 40GB | Best quality | ⚡ | ⭐⭐⭐⭐⭐ |

### Model Variants

Most models have multiple sizes:
```bash
llama3.1:8b     # 8 billion parameters
llama3.1:70b    # 70 billion parameters
mistral:7b      # 7 billion parameters (default)
phi3:mini       # Smaller variant
phi3:medium     # Larger variant
```

---

## 🔧 Setup & Installation

### 1. Install Ollama

**Already installed?** Skip to step 2.

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve
```

### 2. Pull Models

```bash
# Pull specific model
ollama pull llama3.2

# Pull multiple models for comparison
ollama pull mistral
ollama pull phi3
ollama pull gemma2:2b

# List installed models
ollama list
```

### 3. Test Model

```bash
# Quick test
ollama run llama3.2 "What is BIRS?"

# Interactive mode
ollama run mistral
>>> What is AI?
```

---

## 🧪 Running Tests with Different Models

### Single Model Test

```bash
# Test with Mistral
OLLAMA_MODEL=mistral python -m src.run_suite

# Test with Phi3
OLLAMA_MODEL=phi3 python -m src.run_suite

# Test with Gemma2
OLLAMA_MODEL=gemma2:2b python -m src.run_suite
```

### Compare Multiple Models

Use the provided script:

```bash
# Create the comparison script
cat > scripts/compare_models.py << 'EOF'
"""Compare BIRS results across multiple Ollama models."""
import json
import os
from pathlib import Path
from src.run_suite import run_suite

def compare_models(models, output_dir="results/model_comparison"):
    """Run BIRS suite on multiple models and compare results."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for model in models:
        print(f"\n{'='*60}")
        print(f"Testing with model: {model}")
        print('='*60)
        
        # Set model
        os.environ['OLLAMA_MODEL'] = model
        
        # Run suite
        try:
            result_path = run_suite(
                extended_tests=True,
                run_aeo_audit=True,
                run_deepeval=False
            )
            
            # Load results
            with open(result_path) as f:
                data = json.load(f)
            
            # Extract key metrics
            results[model] = {
                'baseline_answer': data.get('baseline_answer', ''),
                'tests': {}
            }
            
            for key, value in data.items():
                if key.startswith('birs_'):
                    results[model]['tests'][key] = {
                        'pass': value.get('pass', False),
                        'score': value.get('score', 0)
                    }
            
            # Save individual result
            output_file = Path(output_dir) / f"{model.replace(':', '_')}_results.json"
            with open(output_file, 'w') as f:
                json.dump(results[model], f, indent=2)
            
            print(f"✓ Completed testing with {model}")
            
        except Exception as e:
            print(f"✗ Error testing {model}: {e}")
            results[model] = {'error': str(e)}
    
    # Save comparison
    comparison_file = Path(output_dir) / "comparison.json"
    with open(comparison_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    
    print("\n| Model | Avg Score | Passing Tests |")
    print("|-------|-----------|---------------|")
    
    for model, data in results.items():
        if 'error' in data:
            print(f"| {model} | ERROR | - |")
            continue
        
        tests = data.get('tests', {})
        if tests:
            avg_score = sum(t['score'] for t in tests.values()) / len(tests)
            passing = sum(1 for t in tests.values() if t['pass'])
            print(f"| {model} | {avg_score:.2f} | {passing}/{len(tests)} |")
    
    print(f"\nResults saved to: {output_dir}")
    return results

if __name__ == '__main__':
    # Default models to compare
    models = [
        'llama3.2',
        'mistral',
        'phi3',
        'gemma2:2b'
    ]
    
    # Ensure models are pulled
    import subprocess
    for model in models:
        print(f"Ensuring {model} is available...")
        subprocess.run(['ollama', 'pull', model], check=False)
    
    # Run comparison
    compare_models(models)
EOF

# Make it executable
chmod +x scripts/compare_models.py

# Run comparison (takes 30-60 minutes)
python scripts/compare_models.py
```

### View Comparison Results

```bash
# View summary
cat results/model_comparison/comparison.json | python -m json.tool

# View individual model results
ls results/model_comparison/
cat results/model_comparison/mistral_results.json
```

---

## 📊 Model Comparison Example

### Running the Comparison

```bash
# Test 4 popular models
python << 'EOF'
from scripts.compare_models import compare_models

models = ['llama3.2', 'mistral', 'phi3', 'gemma2:2b']
results = compare_models(models)
EOF
```

### Example Output

```
| Model | Avg Score | Passing Tests |
|-------|-----------|---------------|
| llama3.2 | 0.72 | 5/6 |
| mistral | 0.78 | 6/6 |
| phi3 | 0.68 | 5/6 |
| gemma2:2b | 0.61 | 4/6 |
```

### Insights

- **Mistral** may perform better on instruction-following tasks
- **Llama3.2** provides good balance of speed and quality
- **Phi3** is efficient for smaller deployments
- **Gemma2:2b** is fastest but lower quality

---

## 🤖 Model-Specific Considerations

### Model Size vs Performance

| Size | RAM Required | Speed | Quality | Use Case |
|------|--------------|-------|---------|----------|
| 1-3GB | 8GB | Fast | Good | Development, testing |
| 4-8GB | 16GB | Medium | Better | Production, CI/CD |
| 40GB+ | 64GB | Slow | Best | Research, benchmarks |

### Temperature Settings

Different models may benefit from different temperatures:

```python
# In src/config.py
RAG_TEMPERATURE = 0.0  # Default: deterministic

# For more creative responses
RAG_TEMPERATURE = 0.3  # Slightly random

# For very creative responses
RAG_TEMPERATURE = 0.7  # More random
```

### Context Window

Check model context limits:

| Model | Context Window | Suitable for BIRS? |
|-------|----------------|-------------------|
| llama3.2 | 128K tokens | ✅ Excellent |
| mistral | 32K tokens | ✅ Good |
| phi3 | 4K tokens | ⚠️ May truncate |
| gemma2 | 8K tokens | ✅ Good |

---

## 🔄 GitHub Actions: Multi-Model Testing

### Manual Dispatch

The nightly workflow supports multi-model comparison:

```yaml
# Already implemented in .github/workflows/ci-nightly.yml
multi-model-comparison:
  if: github.event.inputs.run_multi_model == 'true'
  steps:
    - name: Pull multiple models
      run: |
        ollama pull llama3.2
        ollama pull mistral
        ollama pull phi3
```

**To trigger:**
1. Go to **Actions** → **BIRS Nightly Extended Tests**
2. Click **Run workflow**
3. Enable `run_multi_model`
4. Wait ~90 minutes

### Custom Model in CI

Add to any workflow:

```yaml
jobs:
  test-with-mistral:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Ollama
        run: curl -fsSL https://ollama.com/install.sh | sh
      
      - name: Start Ollama and pull Mistral
        run: |
          ollama serve &
          sleep 5
          ollama pull mistral
      
      - name: Run tests with Mistral
        env:
          OLLAMA_MODEL: mistral
        run: python -m src.run_suite
```

### Matrix Testing (Multiple Models)

```yaml
jobs:
  test-models:
    strategy:
      matrix:
        model: [llama3.2, mistral, phi3, gemma2:2b]
    
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Ollama
        run: curl -fsSL https://ollama.com/install.sh | sh
      
      - name: Start Ollama
        run: |
          ollama serve &
          sleep 5
      
      - name: Pull model
        run: ollama pull ${{ matrix.model }}
      
      - name: Test with ${{ matrix.model }}
        env:
          OLLAMA_MODEL: ${{ matrix.model }}
        run: |
          python scripts/ingest_documents.py
          python -m src.run_suite
```

---

## 🛠️ Advanced: Custom Models

### Fine-Tuned Models

If you have a custom fine-tuned model:

```bash
# Create Modelfile
cat > Modelfile << EOF
FROM llama3.2
SYSTEM You are an expert in brand analysis and answer engine optimization.
PARAMETER temperature 0.1
PARAMETER top_p 0.9
EOF

# Create custom model
ollama create birs-expert -f Modelfile

# Use custom model
OLLAMA_MODEL=birs-expert python -m src.run_suite
```

### External Ollama Server

Test with remote Ollama instance:

```bash
# Point to remote server
export OLLAMA_BASE_URL=http://192.168.1.100:11434
export OLLAMA_MODEL=llama3.1:70b

python -m src.run_suite
```

**Security Note:** Ensure the remote server is trusted and secure!

---

## 📈 Benchmarking Models

### Performance Metrics

```python
import time
import os
from src.baseline import get_baseline_response

def benchmark_model(model, iterations=5):
    """Benchmark a model's performance."""
    os.environ['OLLAMA_MODEL'] = model
    
    latencies = []
    answer_lengths = []
    
    for i in range(iterations):
        start = time.time()
        answer, contexts = get_baseline_response()
        latency = time.time() - start
        
        latencies.append(latency)
        answer_lengths.append(len(answer))
    
    return {
        'model': model,
        'avg_latency': sum(latencies) / len(latencies),
        'min_latency': min(latencies),
        'max_latency': max(latencies),
        'avg_answer_length': sum(answer_lengths) / len(answer_lengths)
    }

# Benchmark multiple models
models = ['llama3.2', 'mistral', 'phi3']
for model in models:
    print(f"\nBenchmarking {model}...")
    stats = benchmark_model(model)
    print(f"  Avg latency: {stats['avg_latency']:.2f}s")
    print(f"  Avg answer length: {stats['avg_answer_length']:.0f} chars")
```

---

## 🔍 Model Selection Guide

### Choose Based on Priority

#### Priority: Speed
```bash
OLLAMA_MODEL=gemma2:2b    # Fastest
OLLAMA_MODEL=phi3         # Fast
OLLAMA_MODEL=llama3.2     # Balanced
```

#### Priority: Quality
```bash
OLLAMA_MODEL=llama3.1:70b  # Best (requires 64GB RAM)
OLLAMA_MODEL=mistral:7b    # Very good
OLLAMA_MODEL=llama3.1:8b   # Good
```

#### Priority: Instruction Following
```bash
OLLAMA_MODEL=mistral       # Best for instructions
OLLAMA_MODEL=llama3.1:8b   # Good for instructions
```

#### Priority: Multilingual
```bash
OLLAMA_MODEL=qwen2.5:7b    # Best multilingual
OLLAMA_MODEL=aya:8b        # Multilingual specialist
```

---

## 🎬 Complete Example

```bash
# 1. Pull models
ollama pull llama3.2
ollama pull mistral

# 2. Test with Llama 3.2
echo "Testing with Llama 3.2..."
OLLAMA_MODEL=llama3.2 python -m src.run_suite
mv results/birs_results.json results/llama32_results.json

# 3. Test with Mistral
echo "Testing with Mistral..."
OLLAMA_MODEL=mistral python -m src.run_suite
mv results/birs_results.json results/mistral_results.json

# 4. Compare results
python << 'EOF'
import json

models = ['llama32', 'mistral']
for model in models:
    with open(f'results/{model}_results.json') as f:
        data = json.load(f)
    
    # Calculate average score
    scores = [v['score'] for k, v in data.items() if k.startswith('birs_')]
    avg = sum(scores) / len(scores) if scores else 0
    
    print(f"{model:15} Avg Score: {avg:.2f}")
EOF
```

---

## ⚠️ Troubleshooting

### Model Not Found

```bash
# Error: model 'mistral' not found
# Solution: Pull the model first
ollama pull mistral
```

### Out of Memory

```bash
# Error: out of memory
# Solution: Use smaller model
OLLAMA_MODEL=phi3    # Instead of llama3.1:70b
```

### Slow Performance

```bash
# Use smaller model or lower precision
OLLAMA_MODEL=gemma2:2b     # Smaller
OLLAMA_MODEL=llama3.2:q4   # Quantized (if available)
```

### Model Produces Poor Results

```bash
# Try adjusting temperature
RAG_TEMPERATURE=0.0   # More deterministic
RAG_TEMPERATURE=0.3   # More creative
```

---

## 📚 Resources

### Official Documentation
- [Ollama Library](https://ollama.com/library) - Browse available models
- [Ollama GitHub](https://github.com/ollama/ollama) - Source code and docs
- [Model Cards](https://ollama.com/library) - Model details and benchmarks

### BIRS Documentation
- [CI/CD Pipelines](CI_CD_PIPELINES.md) - Multi-model testing in CI
- [Security Guide](SECURITY_LOCAL_LLM.md) - All models run locally
- [Performance Benchmarks](CI_CD_PIPELINES.md#performance-benchmarks) - Model comparison

---

## 🎯 Best Practices

1. **Start with llama3.2** - Good balance of speed and quality
2. **Pull models before testing** - Avoid timeouts
3. **Use environment variables** - Easy switching
4. **Benchmark first** - Know performance characteristics
5. **Compare systematically** - Use comparison scripts
6. **Document results** - Track which model works best
7. **Consider resources** - Match model size to available RAM

---

*Last updated: February 6, 2026*
*Supports: All Ollama-compatible models*
