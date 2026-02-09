"""Compare BIRS results across multiple Ollama models."""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from src.run_suite import run_suite


def compare_models(models, output_dir="results/model_comparison"):
    """Run BIRS suite on multiple models and compare results.

    Args:
        models: List of Ollama model names to compare
        output_dir: Directory to save comparison results

    Returns:
        dict: Comparison results for all models
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    results = {}

    print("\n" + "=" * 60)
    print(f"COMPARING {len(models)} MODELS")
    print("=" * 60)

    for i, model in enumerate(models, 1):
        print(f"\n[{i}/{len(models)}] Testing model: {model}")
        print("-" * 60)

        # Set model via environment variable
        os.environ["OLLAMA_MODEL"] = model

        try:
            # Run the test suite
            suite_results = run_suite()

            # Save individual model results
            model_file = Path(output_dir) / f"{model.replace(':', '_')}_results.json"
            with open(model_file, "w") as f:
                json.dump(suite_results, f, indent=2)

            results[model] = suite_results
            print(f"✓ {model} complete")

        except Exception as e:
            print(f"✗ {model} failed: {e}")
            results[model] = {"error": str(e)}

    # Save comparison summary
    comparison_file = Path(output_dir) / "comparison.json"
    comparison_data = {
        "timestamp": datetime.now().isoformat(),
        "models_tested": len(models),
        "results": results,
    }

    with open(comparison_file, "w") as f:
        json.dump(comparison_data, f, indent=2)

    # Print summary table
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)

    print("\n| Model | Avg Score | Passing Tests | Status |")
    print("|-------|-----------|---------------|--------|")

    for model, data in results.items():
        if "error" in data:
            print(f"| {model} | ERROR | - | ✗ |")
            continue

        tests = data.get("tests", {})
        if tests:
            avg_score = sum(t["score"] for t in tests.values()) / len(tests)
            passing = sum(1 for t in tests.values() if t["pass"])
            status = "✓" if passing == len(tests) else "⚠"
            print(f"| {model} | {avg_score:.2f} | {passing}/{len(tests)} | {status} |")

    print(f"\n📁 Results saved to: {output_dir}")
    print(f"📊 Summary: {comparison_file}")

    # Generate comparison visualization
    _generate_comparison_html(results, output_dir)

    return results


def ensure_models_available(models):
    """Pull models from Ollama if not already available."""
    print("\n" + "=" * 60)
    print("CHECKING MODEL AVAILABILITY")
    print("=" * 60 + "\n")

    for model in models:
        print(f"Ensuring {model} is available...")
        result = subprocess.run(
            ["ollama", "pull", model], capture_output=True, text=True
        )

        if result.returncode == 0:
            print(f"✓ {model} ready")
        else:
            print(f"⚠ {model} pull failed (may already be available)")


def _generate_comparison_html(results: dict, output_dir: str):
    """Generate interactive HTML comparison of multiple models."""
    try:
        from src.visualize import generate_html_report

        print("\n📊 Generating comparison visualizations...")

        # Generate individual reports
        output_path = Path(output_dir)
        for model in results.keys():
            if "error" not in results[model]:
                model_file = output_path / f"{model.replace(':', '_')}_results.json"
                if model_file.exists():
                    html_path = generate_html_report(model_file)
                    print(f"  ✓ {model}: {html_path.name}")

        # Generate comparison dashboard
        comparison_html = _build_comparison_dashboard(results, output_dir)
        comparison_path = output_path / "comparison.html"
        with open(comparison_path, "w", encoding="utf-8") as f:
            f.write(comparison_html)

        print(f"\n🎉 Comparison dashboard: {comparison_path}")

    except Exception as e:
        print(f"⚠️ Could not generate visualizations: {e}")


def _build_comparison_dashboard(results: dict, output_dir: str) -> str:
    """Build comparison dashboard HTML."""
    from datetime import datetime

    # Extract metrics for all models
    model_metrics = {}
    for model, data in results.items():
        if "error" in data:
            continue

        scoring = data.get("scoring", {})
        tests = data.get("tests", {})

        model_metrics[model] = {
            "sentiment_drift": abs(scoring.get("sentiment_drift", 0)),
            "citation_fidelity": scoring.get("citation_fidelity", 0),
            "liar_score": scoring.get("liar_score", 0),
            "avg_score": (
                sum(t.get("score", 0) for t in tests.values()) / len(tests)
                if tests
                else 0
            ),
            "pass_rate": (
                sum(1 for t in tests.values() if t.get("pass", False)) / len(tests)
                if tests
                else 0
            ),
            "tests_passed": sum(1 for t in tests.values() if t.get("pass", False)),
            "tests_total": len(tests),
        }

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BIRS Model Comparison</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .chart-section {{
            margin: 30px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 12px;
        }}
        
        .chart-section h2 {{
            color: #667eea;
            margin-bottom: 20px;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .model-links {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 30px;
        }}
        
        .model-link {{
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            color: #333;
            font-weight: 600;
            transition: transform 0.3s ease;
        }}
        
        .model-link:hover {{
            transform: translateY(-5px);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Multi-Model Comparison</h1>
            <p>BIRS Test Results Across {len(model_metrics)} Models</p>
            <p style="font-size: 0.9em; opacity: 0.9; margin-top: 10px;">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
        
        <div class="content">
            <!-- Pass Rate Comparison -->
            <div class="chart-section">
                <h2>🎯 Test Pass Rates</h2>
                <div class="chart-container">
                    <div id="passRateChart"></div>
                </div>
            </div>
            
            <!-- Average Scores -->
            <div class="chart-section">
                <h2>📊 Average Test Scores</h2>
                <div class="chart-container">
                    <div id="avgScoreChart"></div>
                </div>
            </div>
            
            <!-- Robustness Metrics -->
            <div class="chart-section">
                <h2>🛡️ Robustness Metrics</h2>
                <div class="chart-container">
                    <div id="robustnessChart"></div>
                </div>
            </div>
            
            <!-- Individual Reports -->
            <div class="chart-section">
                <h2>📄 Individual Model Reports</h2>
                <div class="model-links">
                    {_generate_model_links(results)}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Pass Rate Chart
        const passRateData = [{{
            x: {json.dumps(list(model_metrics.keys()))},
            y: {json.dumps([m['pass_rate'] * 100 for m in model_metrics.values()])},
            type: 'bar',
            marker: {{
                color: {json.dumps([m['pass_rate'] for m in model_metrics.values()])},
                colorscale: [[0, '#ef4444'], [0.5, '#fbbf24'], [1, '#10b981']],
                cmin: 0,
                cmax: 1
            }},
            text: {json.dumps([f"{m['tests_passed']}/{m['tests_total']}" for m in model_metrics.values()])},
            textposition: 'auto',
        }}];
        
        const passRateLayout = {{
            title: 'Test Pass Rate by Model',
            yaxis: {{ title: 'Pass Rate (%)', range: [0, 100] }},
            xaxis: {{ title: 'Model' }},
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: 'white',
            font: {{ family: 'system-ui, sans-serif' }},
            showlegend: false,
            height: 400
        }};
        
        Plotly.newPlot('passRateChart', passRateData, passRateLayout, {{responsive: true}});
        
        // Average Score Chart
        const avgScoreData = [{{
            x: {json.dumps(list(model_metrics.keys()))},
            y: {json.dumps([m['avg_score'] for m in model_metrics.values()])},
            type: 'bar',
            marker: {{ color: '#667eea' }},
            text: {json.dumps([f"{m['avg_score']:.2f}" for m in model_metrics.values()])},
            textposition: 'auto',
        }}];
        
        const avgScoreLayout = {{
            title: 'Average Test Score by Model',
            yaxis: {{ title: 'Average Score', range: [0, 1] }},
            xaxis: {{ title: 'Model' }},
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: 'white',
            font: {{ family: 'system-ui, sans-serif' }},
            showlegend: false,
            height: 400
        }};
        
        Plotly.newPlot('avgScoreChart', avgScoreData, avgScoreLayout, {{responsive: true}});
        
        // Robustness Chart (Grouped Bar)
        const robustnessData = [
            {{
                name: 'Sentiment Stability',
                x: {json.dumps(list(model_metrics.keys()))},
                y: {json.dumps([1 - m['sentiment_drift'] for m in model_metrics.values()])},
                type: 'bar',
                marker: {{ color: '#10b981' }}
            }},
            {{
                name: 'Citation Fidelity',
                x: {json.dumps(list(model_metrics.keys()))},
                y: {json.dumps([m['citation_fidelity'] for m in model_metrics.values()])},
                type: 'bar',
                marker: {{ color: '#3b82f6' }}
            }},
            {{
                name: 'Lie Resistance',
                x: {json.dumps(list(model_metrics.keys()))},
                y: {json.dumps([1 - m['liar_score'] for m in model_metrics.values()])},
                type: 'bar',
                marker: {{ color: '#f59e0b' }}
            }}
        ];
        
        const robustnessLayout = {{
            title: 'Robustness Metrics Comparison (Higher is Better)',
            yaxis: {{ title: 'Score', range: [0, 1] }},
            xaxis: {{ title: 'Model' }},
            barmode: 'group',
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: 'white',
            font: {{ family: 'system-ui, sans-serif' }},
            height: 500
        }};
        
        Plotly.newPlot('robustnessChart', robustnessData, robustnessLayout, {{responsive: true}});
    </script>
</body>
</html>"""

    return html


def _generate_model_links(results: dict) -> str:
    """Generate links to individual model reports."""
    links = []
    for model in results.keys():
        if "error" not in results[model]:
            filename = f"{model.replace(':', '_')}_results.html"
            links.append(f'<a href="{filename}" class="model-link">📊 {model}</a>')
    return "\n".join(links)


if __name__ == "__main__":
    # Default models to compare (fast, medium, high-quality)
    default_models = [
        "llama3.2",  # Default BIRS model (balanced)
        "mistral",  # Good instruction following
        "phi3",  # Efficient small model
        "gemma2:2b",  # Very fast, lower quality
    ]

    print("\n🔬 BIRS Multi-Model Comparison")
    print("This will test multiple Ollama models and compare results.")
    print(f"Models: {', '.join(default_models)}")
    print("\nNote: This may take 30-60 minutes depending on hardware.\n")

    # Ensure models are available
    ensure_models_available(default_models)

    # Run comparison
    results = compare_models(default_models)

    print("\n✅ Comparison complete!")
