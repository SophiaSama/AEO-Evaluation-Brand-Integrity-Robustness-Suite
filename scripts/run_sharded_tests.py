#!/usr/bin/env python3
"""
BIRS Test Sharding Runner
Run tests in parallel shards locally for faster development feedback.

Usage:
    python scripts/run_sharded_tests.py --shards 4
    python scripts/run_sharded_tests.py --shards 2 --python-version 3.11
    python scripts/run_sharded_tests.py --list-only
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Fix Unicode support on Windows
if sys.platform == "win32":
    try:
        # Try to set UTF-8 encoding for Windows console
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")
    except:
        pass


def run_shard(
    shard_id: int, total_shards: int, python_exe: str = "python"
) -> tuple[int, str, float]:
    """Run a single test shard."""
    start_time = time.time()

    cmd = [
        python_exe,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--splits",
        str(total_shards),
        "--group",
        str(shard_id),
        "--store-durations",
        "--durations-path=.test_durations",
        "-m",
        "not integration and not e2e",
    ]

    print(f"[>>] Starting shard {shard_id}/{total_shards}...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        duration = time.time() - start_time

        if result.returncode == 0:
            status = f"[OK] Shard {shard_id}/{total_shards} PASSED ({duration:.2f}s)"
        else:
            status = f"[FAIL] Shard {shard_id}/{total_shards} FAILED ({duration:.2f}s)"

        return result.returncode, status, duration

    except Exception as e:
        duration = time.time() - start_time
        return 1, f"[ERROR] Shard {shard_id}/{total_shards} ERROR: {e}", duration


def list_test_files():
    """List all test files that will be sharded."""
    test_dir = Path("tests")
    test_files = sorted(test_dir.glob("test_*.py"))

    print("Test files to be sharded:")
    for i, test_file in enumerate(test_files, 1):
        lines = len(test_file.read_text().splitlines())
        print(f"  {i}. {test_file.name} ({lines} lines)")

    print(f"\n Total: {len(test_files)} test files")
    return len(test_files)


def main():
    parser = argparse.ArgumentParser(
        description="Run BIRS tests in parallel shards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Run tests with 4 shards (recommended):
    python scripts/run_sharded_tests.py --shards 4
  
  Run tests with 2 shards:
    python scripts/run_sharded_tests.py --shards 2
  
  List test files without running:
    python scripts/run_sharded_tests.py --list-only
  
  Run with specific Python version:
    python scripts/run_sharded_tests.py --shards 4 --python-version python3.11
        """,
    )

    parser.add_argument(
        "--shards", type=int, default=4, help="Number of parallel shards (default: 4)"
    )

    parser.add_argument(
        "--python-version",
        type=str,
        default="python",
        help="Python executable to use (default: python)",
    )

    parser.add_argument(
        "--list-only", action="store_true", help="List test files without running them"
    )

    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Run shards sequentially instead of parallel",
    )

    args = parser.parse_args()

    # List mode
    if args.list_only:
        list_test_files()
        return 0

    # Validate Python version
    try:
        result = subprocess.run(
            [args.python_version, "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"[Python] Using: {result.stdout.strip()}")
    except Exception as e:
        print(f"[ERROR] Python executable '{args.python_version}' not found")
        return 1

    # Check dependencies
    print("[Setup] Checking dependencies...")
    try:
        subprocess.run(
            [
                args.python_version,
                "-m",
                "pip",
                "install",
                "-q",
                "pytest-split",
                "pytest-xdist",
            ],
            check=True,
        )
    except:
        print(
            "[WARN] Warning: Could not install pytest-split. Make sure it's installed."
        )

    print(f"\n[Tests] Running tests with {args.shards} shards...")
    print("=" * 60)

    start_time = time.time()

    if args.sequential:
        # Run shards sequentially
        results = []
        for shard_id in range(1, args.shards + 1):
            returncode, status, duration = run_shard(
                shard_id, args.shards, args.python_version
            )
            print(status)
            results.append((returncode, status, duration))
    else:
        # Run shards in parallel
        with ThreadPoolExecutor(max_workers=args.shards) as executor:
            futures = {
                executor.submit(
                    run_shard, shard_id, args.shards, args.python_version
                ): shard_id
                for shard_id in range(1, args.shards + 1)
            }

            results = []
            for future in as_completed(futures):
                returncode, status, duration = future.result()
                print(status)
                results.append((returncode, status, duration))

    total_time = time.time() - start_time

    # Summary
    print("\n" + "=" * 60)
    print("[Summary] Test Summary:")
    print("=" * 60)

    passed = sum(1 for r in results if r[0] == 0)
    failed = sum(1 for r in results if r[0] != 0)

    print(f"[OK] Passed: {passed}/{args.shards} shards")
    print(f"[FAIL] Failed: {failed}/{args.shards} shards")
    print(f"[Time] Total time: {total_time:.2f}s")

    if args.sequential:
        avg_time = total_time / args.shards
        print(f"[Time] Average time per shard: {avg_time:.2f}s")
    else:
        max_time = max(r[2] for r in results)
        print(f"[Time] Longest shard: {max_time:.2f}s")
        speedup = sum(r[2] for r in results) / total_time
        print(f"[Speed] Speedup: {speedup:.2f}x")

    if failed > 0:
        print("\n[FAIL] Some tests failed. Run individual shards for details:")
        for i, (returncode, status, _) in enumerate(results, 1):
            if returncode != 0:
                print(f"   pytest tests/ --splits {args.shards} --group {i}")
        return 1

    print("\n[OK] All tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
