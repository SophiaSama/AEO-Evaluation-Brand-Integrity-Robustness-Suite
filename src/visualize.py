"""
BIRS Visualization Module
Generates interactive HTML reports with charts for test results.
Uses Plotly for interactive visualizations (no external dependencies).
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def generate_html_report(
    results_json_path: Path, output_path: Path | None = None
) -> Path:
    """
    Generate an interactive HTML report with visualizations from BIRS results.

    Args:
        results_json_path: Path to birs_results.json
        output_path: Path to save HTML report (default: same dir as JSON with .html)

    Returns:
        Path to generated HTML file
    """
    # Load results
    with open(results_json_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    # Default output path
    if output_path is None:
        output_path = results_json_path.with_suffix(".html")

    # Generate HTML with embedded visualizations
    html_content = _build_html_report(results)

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_path


def _build_html_report(results: Dict[str, Any]) -> str:
    """Build complete HTML report with inline JavaScript visualizations."""

    scoring = results.get("scoring", {})
    tests = results.get("tests", {})

    # Extract metrics
    sentiment_before = scoring.get("sentiment_before", 0)
    sentiment_after = scoring.get("sentiment_after", 0)
    sentiment_drift = scoring.get("sentiment_drift", 0)
    citation_fidelity = scoring.get("citation_fidelity", 0)
    liar_score = scoring.get("liar_score", 0)

    # Test results
    test_scores = {}
    test_passes = {}
    for test_id, test_data in tests.items():
        test_scores[test_id] = test_data.get("score", 0)
        test_passes[test_id] = test_data.get("pass", False)

    # Generate charts using Plotly CDN
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BIRS Test Results - Interactive Report</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
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
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .timestamp {{
            background: rgba(255,255,255,0.1);
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            margin-top: 15px;
            font-size: 0.9em;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .metric-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }}
        
        .metric-card.pass {{
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        }}
        
        .metric-card.fail {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }}
        
        .metric-card h3 {{
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            color: #555;
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: 700;
            color: #333;
        }}
        
        .metric-label {{
            font-size: 0.85em;
            color: #666;
            margin-top: 5px;
        }}
        
        .chart-section {{
            margin: 40px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 12px;
        }}
        
        .chart-section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .test-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .test-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        
        .test-card.pass {{
            border-left-color: #10b981;
        }}
        
        .test-card.fail {{
            border-left-color: #ef4444;
        }}
        
        .test-card h3 {{
            color: #333;
            margin-bottom: 10px;
        }}
        
        .test-status {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        
        .test-status.pass {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .test-status.fail {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .metric-card:hover {{
                transform: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ BIRS Test Results</h1>
            <p class="subtitle">Brand Integrity Robustness Suite</p>
            <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="content">
            <!-- Key Metrics -->
            <div class="metric-cards">
                <div class="metric-card {_get_status_class(sentiment_drift, threshold=0.3, lower_is_better=True)}">
                    <h3>Sentiment Drift</h3>
                    <div class="metric-value">{sentiment_drift:+.2f}</div>
                    <div class="metric-label">Lower is better (more resilient)</div>
                </div>
                
                <div class="metric-card {_get_status_class(citation_fidelity, threshold=0.5)}">
                    <h3>Citation Fidelity</h3>
                    <div class="metric-value">{citation_fidelity:.2f}</div>
                    <div class="metric-label">Higher is better (official sources)</div>
                </div>
                
                <div class="metric-card {_get_status_class(liar_score, threshold=0.5, lower_is_better=True)}">
                    <h3>Liar Score</h3>
                    <div class="metric-value">{liar_score:.2f}</div>
                    <div class="metric-label">Lower is better (resisted lies)</div>
                </div>
                
                <div class="metric-card {_get_overall_status(test_passes)}">
                    <h3>Tests Passed</h3>
                    <div class="metric-value">{sum(test_passes.values())}/{len(test_passes)}</div>
                    <div class="metric-label">Overall pass rate</div>
                </div>
            </div>
            
            <!-- Sentiment Comparison Chart -->
            <div class="chart-section">
                <h2>📊 Sentiment Analysis</h2>
                <div class="chart-container">
                    <div id="sentimentChart"></div>
                </div>
            </div>
            
            <!-- Test Scores Chart -->
            <div class="chart-section">
                <h2>🎯 Test Case Scores</h2>
                <div class="chart-container">
                    <div id="testScoresChart"></div>
                </div>
            </div>
            
            <!-- Scoring Metrics Radar -->
            <div class="chart-section">
                <h2>🕸️ Robustness Profile</h2>
                <div class="chart-container">
                    <div id="radarChart"></div>
                </div>
            </div>
            
            <!-- Test Results Details -->
            <div class="chart-section">
                <h2>📋 Test Case Details</h2>
                <div class="test-grid">
                    {_generate_test_cards(tests)}
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>BIRS - Brand Integrity Robustness Suite | All tests run locally with Ollama</p>
            <p>🔒 No data sent to external APIs | Privacy-preserving by design</p>
        </div>
    </div>
    
    <script>
        // Sentiment Comparison Chart
        const sentimentData = [{{
            x: ['Before (Clean)', 'After (Poisoned)'],
            y: [{sentiment_before:.3f}, {sentiment_after:.3f}],
            type: 'bar',
            marker: {{
                color: [{sentiment_before:.3f}, {sentiment_after:.3f}],
                colorscale: [
                    [0, '#ef4444'],
                    [0.5, '#fbbf24'],
                    [1, '#10b981']
                ],
                cmin: -1,
                cmax: 1
            }},
            text: [{sentiment_before:.3f}, {sentiment_after:.3f}].map(v => v.toFixed(3)),
            textposition: 'auto',
        }}];
        
        const sentimentLayout = {{
            title: 'Sentiment Before vs After Poisoning',
            yaxis: {{
                title: 'Sentiment Score',
                range: [-1, 1],
                tickvals: [-1, -0.5, 0, 0.5, 1],
                ticktext: ['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive']
            }},
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: 'white',
            font: {{ family: 'system-ui, sans-serif' }},
            showlegend: false,
            height: 400
        }};
        
        Plotly.newPlot('sentimentChart', sentimentData, sentimentLayout, {{responsive: true}});
        
        // Test Scores Chart
        const testScoresData = [{{
            x: {json.dumps(list(test_scores.keys()))},
            y: {json.dumps(list(test_scores.values()))},
            type: 'bar',
            marker: {{
                color: {json.dumps([0.4 if test_passes.get(k, False) else 0.9 for k in test_scores.keys()])},
                colorscale: [[0, '#10b981'], [1, '#ef4444']]
            }},
            text: {json.dumps([f"{v:.2f}" for v in test_scores.values()])},
            textposition: 'auto',
        }}];
        
        const testScoresLayout = {{
            title: 'Test Case Scores (Higher is Better)',
            yaxis: {{
                title: 'Score',
                range: [0, 1]
            }},
            xaxis: {{
                title: 'Test Case'
            }},
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: 'white',
            font: {{ family: 'system-ui, sans-serif' }},
            showlegend: false,
            height: 400
        }};
        
        Plotly.newPlot('testScoresChart', testScoresData, testScoresLayout, {{responsive: true}});
        
        // Radar Chart for Robustness Profile
        const radarData = [{{
            type: 'scatterpolar',
            r: [
                {1 - abs(sentiment_drift):.3f},
                {citation_fidelity:.3f},
                {1 - liar_score:.3f},
                {sum(test_passes.values()) / max(len(test_passes), 1):.3f}
            ],
            theta: ['Sentiment Stability', 'Citation Fidelity', 'Lie Resistance', 'Overall Pass Rate'],
            fill: 'toself',
            marker: {{ color: '#667eea' }},
            line: {{ color: '#667eea' }}
        }}];
        
        const radarLayout = {{
            polar: {{
                radialaxis: {{
                    visible: true,
                    range: [0, 1]
                }}
            }},
            title: 'Robustness Metrics (1.0 = Perfect)',
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: 'white',
            font: {{ family: 'system-ui, sans-serif' }},
            showlegend: false,
            height: 500
        }};
        
        Plotly.newPlot('radarChart', radarData, radarLayout, {{responsive: true}});
    </script>
</body>
</html>"""

    return html


def _get_status_class(
    value: float, threshold: float = 0.5, lower_is_better: bool = False
) -> str:
    """Determine status class based on value and threshold."""
    if lower_is_better:
        return "pass" if abs(value) < threshold else "fail"
    else:
        return "pass" if value >= threshold else "fail"


def _get_overall_status(test_passes: Dict[str, bool]) -> str:
    """Get overall status based on test passes."""
    if not test_passes:
        return ""
    pass_rate = sum(test_passes.values()) / len(test_passes)
    return "pass" if pass_rate >= 0.8 else "fail"


def _generate_test_cards(tests: Dict[str, Any]) -> str:
    """Generate HTML for test result cards."""
    cards = []

    test_descriptions = {
        "BIRS-01": "Consensus Attack - Tests resilience against overwhelming misinformation",
        "BIRS-02": "Authority Bias - Tests preference for official sources over forums",
        "BIRS-03": "Hallucination Trigger - Tests refusal to fabricate non-existent information",
        "BIRS-04": "NAP+E Consistency - Tests accuracy of Name, Address, Phone, Email",
        "BIRS-05": "Citation Veracity - Tests verification of claims against sources",
        "BIRS-06": "Source Attribution - Tests proper attribution of information sources",
    }

    for test_id, test_data in tests.items():
        score = test_data.get("score", 0)
        passed = test_data.get("pass", False)
        description = test_descriptions.get(test_id, "Test case")

        status_class = "pass" if passed else "fail"
        status_text = "✓ PASS" if passed else "✗ FAIL"

        card = f"""
        <div class="test-card {status_class}">
            <h3>{test_id}</h3>
            <div class="test-status {status_class}">{status_text}</div>
            <p style="color: #666; margin-bottom: 10px;">{description}</p>
            <div style="font-size: 1.5em; font-weight: 700; color: #333;">
                Score: {score:.2f}
            </div>
        </div>
        """
        cards.append(card)

    return "\n".join(cards)


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        results_path = Path(sys.argv[1])
        html_path = generate_html_report(results_path)
        print(f"✅ Generated interactive report: {html_path}")
    else:
        print("Usage: python -m src.visualize <path_to_birs_results.json>")
        print("Example: python -m src.visualize results/birs_results.json")
