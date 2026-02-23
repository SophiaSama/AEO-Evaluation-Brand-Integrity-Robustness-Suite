# Test Sharding Quick Reference

## 🚀 Quick Commands

### Local Testing
```bash
# Run with 4 shards (recommended)
python scripts/run_sharded_tests.py --shards 4

# Run with 2 shards
python scripts/run_sharded_tests.py --shards 2

# List test files
python scripts/run_sharded_tests.py --list-only

# Sequential (debugging)
python scripts/run_sharded_tests.py --shards 4 --sequential
```

### Direct pytest
```bash
# Run specific shard
pytest tests/ --splits 4 --group 2

# Store durations
pytest tests/ --store-durations --durations-path=.test_durations

# Collect only (see distribution)
pytest tests/ --splits 4 --group 1 --collect-only
```

## 📊 Performance

| Shards | Speedup | Use Case |
|--------|---------|----------|
| 2      | ~2x     | Small test suites (<10 tests) |
| 4      | ~3-4x   | **Recommended** for most cases |
| 6      | ~4-5x   | Large test suites (>20 tests) |
| 8      | ~5-6x   | Very large suites (>40 tests) |

## 🔧 Configuration Files

- **pytest.ini**: Test markers and pytest config
- **ci-tests-sharded.yml**: Main sharded workflow
- **.test_durations**: Cached test timing data (auto-generated)

## 📁 Key Files

```
.github/workflows/ci-tests-sharded.yml  # Sharded CI workflow
scripts/run_sharded_tests.py            # Local test runner
pytest.ini                              # pytest configuration
.test_durations                         # Timing cache
```

## 🎯 Workflow Features

✅ Auto-calculates optimal shard count  
✅ Duration-based distribution (smart balancing)  
✅ Parallel execution across Python 3.10, 3.11, 3.12  
✅ Automatic coverage merging  
✅ Manual trigger with custom shard count  
✅ Caches test durations for consistency  

## 🔍 Debugging

```bash
# View test distribution
pytest tests/ --splits 4 --group 1 --collect-only

# Run with verbose output
pytest tests/ --splits 4 --group 2 -vv

# Show slowest tests
pytest tests/ --durations=10

# Run specific shard locally
pytest tests/ --splits 4 --group 3 -v
```

## 📈 Metrics

Check GitHub Actions artifacts:
- `coverage-shard-N-py3.11`: Individual shard coverage
- `code-coverage-merged`: Merged coverage report
- `test-durations-shard-N`: Duration data for optimization

## ⚙️ Dependencies

Required packages (auto-installed in CI):
```bash
pip install pytest pytest-cov pytest-xdist pytest-split
```

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| Unbalanced shards | Increase shard count or check test durations |
| Missing pytest-split | `pip install pytest-split` |
| Coverage gaps | Verify all shards completed successfully |
| Shard timeout | Reduce tests per shard (increase shard count) |

## 📚 Documentation

- [Full Guide](TEST_SHARDING_GUIDE.md)
- [CI/CD Pipelines](CI_CD_PIPELINES.md)
- [CI/CD Quick Wins](CI_CD_QUICK_WINS.md)

## 💡 Tips

1. **First run**: Tests distributed evenly by file count
2. **Subsequent runs**: Uses `.test_durations` for optimal balance
3. **Best practice**: Commit `.test_durations` to repo
4. **Local dev**: Start with 2-4 shards
5. **CI/CD**: Auto-sharding handles optimization
