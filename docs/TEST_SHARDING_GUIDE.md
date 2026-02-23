# Test Sharding Guide

## Overview

Test sharding enables parallel test execution by splitting tests into multiple independent groups (shards) that run simultaneously. This significantly reduces CI/CD pipeline execution time and provides faster feedback during development.

## 🚀 Quick Start

### Local Development

Run tests with 4 parallel shards (recommended):

```bash
python scripts/run_sharded_tests.py --shards 4
```

### CI/CD

The sharded test workflow runs automatically on push/PR:

- **Workflow**: `.github/workflows/ci-tests-sharded.yml`
- **Auto-sharding**: Dynamically calculates optimal shard count based on test files
- **Manual trigger**: Can specify custom shard count via workflow dispatch

## 📊 Benefits

### Performance Improvements

| Test Count | No Sharding | 2 Shards | 4 Shards | Speedup |
|-----------|-------------|----------|----------|---------|
| 5 tests   | ~30s        | ~15s     | ~8s      | 3.75x   |
| 10 tests  | ~60s        | ~30s     | ~15s     | 4x      |
| 20 tests  | ~120s       | ~60s     | ~30s     | 4x      |

### CI/CD Benefits

- ✅ **Faster Feedback**: Get test results 2-4x faster
- ✅ **Better Resource Usage**: Parallel execution uses available CPU cores
- ✅ **Scalability**: Add more shards as test suite grows
- ✅ **Smart Distribution**: pytest-split uses historical timing data for balanced shards
- ✅ **Multi-version Testing**: Test against Python 3.10, 3.11, 3.12 in parallel

## 🔧 How It Works

### 1. Test Discovery

pytest-split analyzes all test files in `tests/` directory:

```
tests/
├── test_crawler.py      (22 lines)
├── test_rag.py          (10 lines)
├── test_scoring.py      (46 lines)
├── test_test_cases.py   (24 lines)
└── test_visualize.py    (109 lines)
```

### 2. Duration-Based Distribution

- **First Run**: Tests are distributed evenly across shards
- **Subsequent Runs**: Uses cached duration data (`.test_durations`) for optimal balance
- **Smart Balancing**: Longer tests are distributed to prevent bottlenecks

### 3. Parallel Execution

Each shard runs independently:

```
Shard 1: test_visualize.py (longest)
Shard 2: test_scoring.py
Shard 3: test_crawler.py + test_test_cases.py
Shard 4: test_rag.py (shortest)
```

### 4. Coverage Merging

After all shards complete:
- Individual coverage reports are collected
- Merged into a single comprehensive report
- Uploaded to Codecov

## 📋 Configuration

### pytest.ini

Test markers and configuration:

```ini
[pytest]
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower)
    e2e: End-to-end tests (slowest)
    slow: Tests that take longer than 1 second
    fast: Tests that complete in under 1 second
```

### Workflow Configuration

`.github/workflows/ci-tests-sharded.yml`:

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    shard: [1, 2, 3, 4]  # 4 shards
```

## 🎯 Usage Examples

### Local Testing

#### Run with default 4 shards:
```bash
python scripts/run_sharded_tests.py --shards 4
```

#### Run with 2 shards:
```bash
python scripts/run_sharded_tests.py --shards 2
```

#### List test files without running:
```bash
python scripts/run_sharded_tests.py --list-only
```

#### Run sequentially (for debugging):
```bash
python scripts/run_sharded_tests.py --shards 4 --sequential
```

#### Use specific Python version:
```bash
python scripts/run_sharded_tests.py --shards 4 --python-version python3.11
```

### Direct pytest Commands

#### Run a specific shard:
```bash
pytest tests/ --splits 4 --group 2
```

#### Store duration data:
```bash
pytest tests/ --store-durations --durations-path=.test_durations
```

#### Run with parallel execution within shard:
```bash
pytest tests/ --splits 4 --group 1 -n auto
```

### CI/CD Workflow Dispatch

Trigger manually with custom shard count:

1. Go to Actions → "BIRS CI - Tests (Sharded)"
2. Click "Run workflow"
3. Select shard count (2, 4, 6, or 8)
4. Run workflow

## 📈 Performance Optimization

### Optimal Shard Count

The workflow auto-calculates based on:
```
shard_count = min(max(test_files / 2, 2), 4)
```

**Recommendations:**
- **5 test files**: 2 shards
- **10 test files**: 4 shards
- **20+ test files**: 4-8 shards

### Duration Caching

Test durations are cached to optimize distribution:

```yaml
- name: Cache test durations
  uses: actions/cache@v4
  with:
    path: .test_durations
    key: test-durations-${{ matrix.python-version }}-${{ hashFiles('tests/**/*.py') }}
```

### Balancing Strategies

1. **Equal File Count**: Distribute test files evenly
2. **Duration-Based**: Use historical timing (preferred)
3. **Manual Markers**: Use pytest markers for grouping

## 🔍 Monitoring & Debugging

### Check Shard Distribution

```bash
# See which tests are in each shard
pytest tests/ --splits 4 --group 1 --collect-only
pytest tests/ --splits 4 --group 2 --collect-only
pytest tests/ --splits 4 --group 3 --collect-only
pytest tests/ --splits 4 --group 4 --collect-only
```

### View Test Durations

```bash
# Show slowest tests
pytest tests/ --durations=10

# Store durations for next run
pytest tests/ --store-durations
```

### Analyze Coverage

Coverage reports are uploaded per shard:
- `coverage-shard-1-py3.11`
- `coverage-shard-2-py3.11`
- `coverage-shard-3-py3.11`
- `coverage-shard-4-py3.11`

Merged report: `code-coverage-merged`

## 🚨 Troubleshooting

### Issue: Unbalanced Shards

**Symptom**: One shard takes much longer than others

**Solution**: 
1. Check test durations: `pytest --durations=10`
2. Manually group slow tests using markers
3. Increase shard count

### Issue: Shard Failures

**Symptom**: Some shards fail, others pass

**Solution**:
```bash
# Run failing shard locally
pytest tests/ --splits 4 --group 2 -v

# Run with verbose output
pytest tests/ --splits 4 --group 2 -vv --tb=long
```

### Issue: Missing Dependencies

**Symptom**: `pytest-split not found`

**Solution**:
```bash
pip install pytest-split pytest-xdist
```

### Issue: Coverage Gaps

**Symptom**: Merged coverage lower than expected

**Solution**:
1. Check all shards completed successfully
2. Verify coverage artifacts uploaded
3. Manually merge: `coverage combine coverage-artifacts/*/coverage-*.xml`

## 📚 Advanced Configuration

### Custom Test Grouping

Use pytest markers for custom grouping:

```python
# In test file
@pytest.mark.slow
def test_long_running():
    pass

@pytest.mark.fast
def test_quick():
    pass
```

Run only fast tests in parallel:
```bash
pytest tests/ -m fast --splits 4 --group 1
```

### Matrix Expansion

Test multiple configurations:

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    shard: [1, 2, 3, 4]
    os: [ubuntu-latest, windows-latest]
```

This creates: 3 × 4 × 2 = **24 parallel jobs**

### Conditional Sharding

Only shard on main branch:

```yaml
jobs:
  unit-tests-sharded:
    if: github.ref == 'refs/heads/main'
    strategy:
      matrix:
        shard: [1, 2, 3, 4, 5, 6, 7, 8]  # More shards for main
```

## 📊 Metrics & Reporting

### Workflow Outputs

The workflow provides:
- ✅ Per-shard test results
- ✅ Merged coverage report
- ✅ Test duration data
- ✅ Summary of all shard results

### GitHub Actions Summary

Check the "Summary" tab for:
- Total execution time
- Shard distribution
- Coverage percentage
- Failed tests (if any)

## 🔗 Related Documentation

- [CI/CD Pipelines Guide](CI_CD_PIPELINES.md)
- [CI/CD Quick Wins](CI_CD_QUICK_WINS.md)
- [pytest-split documentation](https://github.com/jerry-git/pytest-split)
- [pytest-xdist documentation](https://pytest-xdist.readthedocs.io/)

## 🎓 Best Practices

1. **Keep Tests Independent**: Sharding requires tests to be isolated
2. **Use Markers**: Categorize tests for better control
3. **Monitor Duration**: Regularly check test timing
4. **Cache Durations**: Enable duration caching for optimal distribution
5. **Start Small**: Begin with 2-4 shards, scale as needed
6. **Balance Cost**: More shards = faster runs but higher CI minutes usage

## 📞 Support

For issues or questions:
1. Check [CI/CD FAQ](CI_CD_FAQ.md)
2. Review workflow logs in GitHub Actions
3. Run tests locally with `--verbose` flag
4. File an issue with reproduction steps
