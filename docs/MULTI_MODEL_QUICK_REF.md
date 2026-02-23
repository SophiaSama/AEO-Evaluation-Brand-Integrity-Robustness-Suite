# Multi-Model Testing Quick Reference

## 🚀 Quick Start (3 Methods)

### 1. Environment Variable (Fastest)
```powershell
# Windows PowerShell
$env:OLLAMA_MODEL = "mistral"
python -m src.run_suite
```

```bash
# Linux/Mac
export OLLAMA_MODEL=mistral
python -m src.run_suite
```

### 2. Inline (One Command)
```powershell
# Windows PowerShell
$env:OLLAMA_MODEL="phi3"; python -m src.run_suite
```

```bash
# Linux/Mac
OLLAMA_MODEL=phi3 python -m src.run_suite
```

### 3. .env File (Recommended)
Create/edit `.env` in project root:
```
OLLAMA_MODEL=mistral
```

Then run normally:
```bash
python -m src.run_suite
```

---

## 🎯 Popular Models for Testing

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **llama3.2** (default) | 2GB | Fast | Good | General purpose |
| **mistral** | 4GB | Medium | Excellent | Instruction following |
| **phi3** | 2.3GB | Fast | Good | Small deployments |
| **gemma2:2b** | 1.6GB | Very Fast | Fair | Speed testing |
| **llama3.1:70b** | 40GB | Slow | Excellent | Best quality |

---

## 📊 Compare Multiple Models

### Run Comparison Script
```bash
# Compare 4 popular models
python scripts/compare_models.py
```

### Custom Model List
```python
from scripts.compare_models import compare_models

# Test specific models
models = ['llama3.2', 'mistral', 'phi3']
results = compare_models(models)
```

### Results Location
- **Individual results**: `results/model_comparison/<model>_results.json`
- **Comparison summary**: `results/model_comparison/comparison.json`

---

## 🔧 Setup & Installation

### Install Model
```bash
# Pull specific model
ollama pull mistral

# List installed models
ollama list

# Test model interactively
ollama run mistral "Test message"
```

### Verify Configuration
```powershell
# Windows PowerShell
$env:OLLAMA_MODEL="mistral"
python -c "from src.config import OLLAMA_MODEL; print(f'Using model: {OLLAMA_MODEL}')"
```

```bash
# Linux/Mac
OLLAMA_MODEL=mistral python -c "from src.config import OLLAMA_MODEL; print(f'Using model: {OLLAMA_MODEL}')"
```

---

## 🧪 CI/CD Multi-Model Testing

### GitHub Actions Matrix Example
```yaml
strategy:
  matrix:
    model: [llama3.2, mistral, phi3]
steps:
  - name: Test with ${{ matrix.model }}
    run: |
      ollama pull ${{ matrix.model }}
      OLLAMA_MODEL=${{ matrix.model }} python -m src.run_suite
```

### Local Matrix Testing
```bash
# Test multiple models in sequence
for model in llama3.2 mistral phi3; do
  echo "Testing $model..."
  OLLAMA_MODEL=$model python -m src.run_suite
done
```

---

## 📖 Full Documentation

For detailed information, see:
- **[MULTI_MODEL_TESTING.md](../docs/MULTI_MODEL_TESTING.md)** - Complete guide
- **[README.md](../README.md)** - Project overview
- **[CI_CD_PIPELINES.md](../docs/CI_CD_PIPELINES.md)** - CI/CD setup

---

## 💡 Tips

1. **Start small**: Test with `gemma2:2b` or `phi3` first (faster)
2. **Compare systematically**: Use `scripts/compare_models.py` for consistent results
3. **Monitor resources**: Larger models (70b+) need 40GB+ RAM
4. **CI/CD**: Default `llama3.2` balances speed and quality
5. **Production**: Consider `mistral` or `llama3.1:70b` for best quality

---

## ⚠️ Troubleshooting

### Model Not Found
```bash
# Pull the model first
ollama pull <model-name>
ollama list  # Verify installation
```

### Environment Variable Not Working
```powershell
# Windows PowerShell - verify it's set
$env:OLLAMA_MODEL
Get-ChildItem env:OLLAMA_MODEL

# Set and run in one line
$env:OLLAMA_MODEL="mistral"; python -m src.run_suite
```

### Model Performance Issues
- **Too slow**: Use smaller model (`phi3`, `gemma2:2b`)
- **Low quality**: Use larger model (`mistral`, `llama3.1:70b`)
- **Out of memory**: Reduce model size or close other applications

---

**Ready to test?** Start with:
```bash
ollama pull mistral
OLLAMA_MODEL=mistral python -m src.run_suite
```
