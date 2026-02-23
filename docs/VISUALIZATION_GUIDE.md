# 📊 BIRS Visualization Guide

**Interactive HTML Reports for Test Results**

---

## Overview

BIRS now includes comprehensive visualization capabilities that transform JSON test results into interactive HTML reports with charts, graphs, and visual analytics.

### Key Features

✨ **Automatic Generation** - HTML reports generated automatically after tests  
📊 **Interactive Charts** - Hover, zoom, and explore data with Plotly.js  
🎨 **Beautiful Design** - Modern gradient UI with responsive layout  
📈 **Multiple Views** - Sentiment analysis, test scores, robustness profiles  
🔬 **Model Comparison** - Side-by-side comparison dashboard  
🚀 **Zero Dependencies** - Uses CDN-hosted Plotly, no local install needed  

---

## Quick Start

### Option 1: Automatic (Recommended)

Run BIRS test suite - visualization is generated automatically:

```bash
python -m src.run_suite
```

Output:
- `results/birs_results.json` - Test data
- `results/birs_results.html` - **Interactive report** 📊
- `results/birs_report.md` - Markdown summary

### Option 2: Manual Generation

Generate report from existing JSON:

```bash
python scripts/visualize_results.py results/birs_results.json
```

### Option 3: Programmatic

```python
from src.visualize import generate_html_report
from pathlib import Path

html_path = generate_html_report(Path('results/birs_results.json'))
print(f"Report: {html_path}")
```

---

## Report Contents

### 1. **Key Metrics Cards**
Visual cards showing:
- **Sentiment Drift**: How much the model's tone changed
- **Citation Fidelity**: Use of official vs. poisoned sources
- **Liar Score**: Resistance to misinformation
- **Pass Rate**: Overall test success rate

Color-coded: 🟢 Green = Pass, 🔴 Red = Fail

### 2. **Sentiment Analysis Chart**
Bar chart comparing sentiment before/after poisoning:
- **Before**: Sentiment with clean data only
- **After**: Sentiment after poison injection
- Color scale: Red (negative) → Yellow (neutral) → Green (positive)

### 3. **Test Scores Chart**
Bar chart for all test cases (BIRS-01 through BIRS-06):
- Higher scores = better performance
- Color indicates pass/fail status

### 4. **Robustness Profile (Radar Chart)**
Spider/radar chart showing 4 key metrics:
- Sentiment Stability (resistance to tone manipulation)
- Citation Fidelity (preference for official sources)
- Lie Resistance (refusal to repeat misinformation)
- Overall Pass Rate

Perfect score = 1.0 on all axes

### 5. **Test Case Details**
Individual cards for each test:
- Test ID and description
- Pass/Fail status
- Numeric score

---

## Multi-Model Comparison

When comparing models with `scripts/compare_models.py`:

```bash
python scripts/compare_models.py
```

**Generates:**
1. Individual report for each model
2. Comparison dashboard (`results/model_comparison/comparison.html`)

### Comparison Dashboard Shows:

- **Pass Rate Comparison**: Bar chart of test success rates
- **Average Scores**: Overall performance comparison
- **Robustness Metrics**: Grouped bar chart (3 key metrics)
- **Links to Individual Reports**: Quick access to detailed results

---

## CLI Options

### Generate Single Report

```bash
python scripts/visualize_results.py results/birs_results.json
```

### Specify Output Path

```bash
python scripts/visualize_results.py results/birs_results.json -o reports/my_analysis.html
```

### Generate Multiple Reports

```bash
python scripts/visualize_results.py results/*.json
```

### Open in Browser Automatically

```bash
python scripts/visualize_results.py results/birs_results.json --open
```

### Verbose Output

```bash
python scripts/visualize_results.py results/birs_results.json -v
```

---

## Integration with Workflow

### Development Workflow

```bash
# 1. Run tests
python -m src.run_suite

# 2. View interactive report
# Open results/birs_results.html in browser

# 3. Make changes, rerun
python -m src.run_suite

# 4. Compare results
# Reports are timestamped, compare side-by-side
```

### Model Comparison Workflow

```bash
# 1. Compare models
python scripts/compare_models.py

# 2. View comparison dashboard
# Open results/model_comparison/comparison.html

# 3. Explore individual model reports
# Click links in dashboard
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
- name: Run BIRS Tests
  run: python -m src.run_suite

- name: Upload HTML Report
  uses: actions/upload-artifact@v4
  with:
    name: birs-report
    path: results/birs_results.html

- name: Publish to GitHub Pages (optional)
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./results
```

---

## Customization

### Disable Automatic Generation

```python
from src.run_suite import run_suite

# Skip HTML generation
run_suite(generate_html=False)
```

### Custom Styling

Edit `src/visualize.py` to customize:
- Color schemes
- Chart types
- Layout and spacing
- Additional metrics

Example: Change gradient colors
```python
# In src/visualize.py, find:
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

# Change to your colors:
background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
```

---

## Technical Details

### Libraries Used

- **Plotly.js** (via CDN): Interactive charts
- **No local dependencies**: All visualization code is self-contained
- **Modern CSS**: Gradients, flexbox, grid for responsive design

### Browser Compatibility

✅ Chrome, Firefox, Safari, Edge (modern versions)  
✅ Mobile browsers  
📱 Responsive design adapts to screen size  
🖨️ Print-friendly styles included  

### Performance

- **Small files**: ~50-100KB per report
- **Fast loading**: CDN-hosted Plotly
- **Client-side rendering**: No server required
- **Works offline**: After initial CDN load

---

## Visualization Best Practices

### 1. **Accessibility**

Reports include:
- ✅ High contrast colors
- ✅ Clear labels and titles
- ✅ Responsive text sizing
- ✅ Semantic HTML structure

### 2. **Data Clarity**

Charts are designed to:
- Show trends and patterns clearly
- Use appropriate chart types (bar, radar)
- Include context and labels
- Highlight important thresholds

### 3. **Actionable Insights**

Each chart answers a question:
- **Sentiment Chart**: "Was the model swayed?"
- **Test Scores**: "Which tests passed/failed?"
- **Radar**: "What's the overall robustness profile?"
- **Comparison**: "Which model performs best?"

---

## Examples

### Single Model Report

```bash
# Run test
python -m src.run_suite

# Result: results/birs_results.html
# Contains:
# - 4 metric cards (drift, fidelity, liar score, pass rate)
# - 3 interactive charts (sentiment, scores, radar)
# - 6 test case detail cards
```

### Multi-Model Comparison

```bash
# Compare 3 models
python scripts/compare_models.py

# Result: results/model_comparison/
# ├── llama3.2_results.html        (individual)
# ├── mistral_results.html         (individual)
# ├── phi3_results.html            (individual)
# └── comparison.html              (dashboard)
```

---

## Troubleshooting

### "No module named 'src.visualize'"

**Solution**: Run from project root:
```bash
cd d:\projects\AEO_Evaluation
python scripts/visualize_results.py results/birs_results.json
```

### Charts Not Loading

**Solution**: Check internet connection (Plotly CDN required) or open HTML file in browser manually.

### HTML File Opens as Text

**Solution**: Right-click → "Open with" → Browser, or:
```bash
# Windows
start results\birs_results.html

# Linux/Mac
open results/birs_results.html
```

### Styling Issues

**Solution**: Clear browser cache and reload, or try a different browser.

---

## Advanced Usage

### Batch Processing

```bash
# Generate reports for all JSON files
for file in results/archive/*.json; do
    python scripts/visualize_results.py "$file"
done
```

### Integration with Other Tools

```python
# Custom processing
from src.visualize import generate_html_report
import json

# Modify results before visualization
with open('results/birs_results.json', 'r') as f:
    results = json.load(f)

# Add custom metrics
results['custom_metric'] = 0.95

# Save and visualize
with open('results/modified_results.json', 'w') as f:
    json.dump(results, f)

generate_html_report('results/modified_results.json')
```

---

## Future Enhancements

🔮 Planned features:
- Historical trend charts (compare over time)
- Export to PDF
- Custom chart builder
- Real-time dashboard updates
- Integration with web frameworks

---

## Related Documentation

- **[README.md](../README.md)** - Project overview
- **[MULTI_MODEL_TESTING.md](MULTI_MODEL_TESTING.md)** - Model comparison guide
- **[CI_CD_PIPELINES.md](CI_CD_PIPELINES.md)** - Automation setup

---

## Quick Reference

| Task | Command |
|------|---------|
| Generate report | `python scripts/visualize_results.py results/birs_results.json` |
| Open in browser | `python scripts/visualize_results.py results/birs_results.json --open` |
| Multiple files | `python scripts/visualize_results.py results/*.json` |
| Custom output | `python scripts/visualize_results.py input.json -o output.html` |
| Disable auto-gen | `run_suite(generate_html=False)` |

---

**🎉 Start visualizing your test results!**

```bash
python -m src.run_suite
# Then open: results/birs_results.html
```
