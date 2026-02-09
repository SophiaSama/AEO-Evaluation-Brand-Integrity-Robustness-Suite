#!/usr/bin/env python
"""
CLI tool for visualizing BIRS test results.
Generates interactive HTML reports from JSON results.
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate interactive HTML visualizations from BIRS test results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate report from latest results
  python scripts/visualize_results.py results/birs_results.json
  
  # Specify custom output path
  python scripts/visualize_results.py results/birs_results.json -o reports/analysis.html
  
  # Process all JSON files in a directory
  python scripts/visualize_results.py results/*.json
  
  # Generate report and open in browser
  python scripts/visualize_results.py results/birs_results.json --open
        """,
    )

    parser.add_argument("input", nargs="+", help="Path(s) to birs_results.json file(s)")

    parser.add_argument(
        "-o",
        "--output",
        help="Output path for HTML report (default: same name as input with .html)",
    )

    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the generated report in default browser",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Import visualization module
    try:
        from src.visualize import generate_html_report
    except ImportError as e:
        print(f"❌ Error importing visualization module: {e}")
        print("Make sure you're running from the project root directory.")
        return 1

    # Process each input file
    success_count = 0
    for input_path_str in args.input:
        input_path = Path(input_path_str)

        if not input_path.exists():
            print(f"❌ File not found: {input_path}")
            continue

        if not input_path.is_file():
            print(f"❌ Not a file: {input_path}")
            continue

        try:
            # Determine output path
            if args.output and len(args.input) == 1:
                output_path = Path(args.output)
            else:
                output_path = None  # Use default

            if args.verbose:
                print(f"📊 Processing: {input_path}")

            # Generate report
            html_path = generate_html_report(input_path, output_path)

            print(f"✅ Generated: {html_path}")
            success_count += 1

            # Open in browser if requested
            if args.open:
                import webbrowser

                webbrowser.open(f"file://{html_path.absolute()}")
                print(f"🌐 Opened in browser")

        except Exception as e:
            print(f"❌ Error processing {input_path}: {e}")
            if args.verbose:
                import traceback

                traceback.print_exc()

    # Summary
    if success_count > 0:
        print(f"\n🎉 Successfully generated {success_count} report(s)")
        return 0
    else:
        print("\n❌ No reports generated")
        return 1


if __name__ == "__main__":
    sys.exit(main())
