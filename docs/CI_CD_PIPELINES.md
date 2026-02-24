# BIRS CI/CD Pipeline Documentation

## Overview

BIRS uses a comprehensive CI/CD pipeline with 8 specialized workflows covering testing, quality assurance, performance monitoring, and release management.

**🔧 Infrastructure:** All workflows run on **GitHub-hosted Ubuntu runners** (virtual machines) - **no Docker required!** This provides faster startup, better caching, and simpler configuration. See [Docker Optional Guide](CI_CD_DOCKER_OPTIONAL.md) if you need containerization.

## Workflow Summary

| Workflow | Trigger | Duration | Purpose |
|----------|---------|----------|---------|
| **ci-tests-sharded.yml** | Push, PR | ~10 min | Linting, sharded unit tests, integration tests |
| **ci-structure-security.yml** | Push, PR | ~4 min | Structure validation, security scan |
| **ci-integration.yml** | Push to main/develop, Nightly | ~30 min | Integration & E2E tests with Ollama |
| **ci-dependencies.yml** | Daily, PR (requirements.txt) | ~15 min | Security audit, outdated packages, licenses |
| **ci-performance.yml** | Weekly, Manual | ~45 min | RAG benchmarks, embedding performance |
| _Benchmark history updates are sent as pull requests (no direct pushes to `main`)_ |
| **ci-docs.yml** | Push, PR | ~10 min | Doc validation, API generation, GitHub Pages |
| **ci-quality.yml** | Push, PR, Weekly | ~20 min | Coverage, complexity, maintainability, tech debt |
| **ci-nightly.yml** | Nightly, Manual | ~60 min | Extended AEO tests, multi-model comparison |
| **crawler-test.yml** | Weekly, Manual | ~10 min | Web crawler validation |
| **release.yml** | Tag push, Manual | ~15 min | Release validation & GitHub release |

---

## Detailed Workflow Documentation

### 1. CI Tests (Sharded) (`ci-tests-sharded.yml`)

**Purpose:** Fast feedback on code quality and basic functionality

**Triggers:**
- Push to: `main`, `develop`, `feat/*`, `fix/*`
- Pull requests to: `main`, `develop`

**Jobs:**

#### `lint`
- **Tools:** Black, isort, Flake8, mypy
- **Checks:**
  - Code formatting (Black)
  - Import sorting (isort)
  - Style violations (Flake8)
  - Type hints (mypy, non-blocking)
- **Duration:** ~2 min

#### `unit-tests-sharded`
- **Matrix:** Python 3.10, 3.11, 3.12
- **Tools:** pytest, pytest-cov, pytest-split
- **Features:**
  - Sharded test execution (parallel shards)
  - Code coverage per shard, merged into a single report
  - HTML coverage reports
- **Duration:** ~5 min per Python version

#### `integration-tests`
- **Tools:** pytest, pytest-cov
- **Scope:** `-m "integration"` (non-blocking)
- **Duration:** ~5 min

#### Related: Structure & Security (`ci-structure-security.yml`)
- **Jobs:** `structure-validation`, `security-scan`
- **Purpose:** Validate data structure and run Bandit/Safety scans
- **Duration:** ~4 min

---

### 2. Integration Tests (`ci-integration.yml`)

**Purpose:** Validate full system with real LLM and vector database

**Triggers:**
- Push to: `main`, `develop`
- Pull requests to: `main`
- Nightly at 2 AM UTC
- Manual dispatch

**Jobs:**

#### `integration-tests`
- **Setup:**
  - Installs Ollama
  - Pulls Llama 3.2 model (~30 min first run)
  - Populates ChromaDB via ingestion
- **Tests:**
  - Integration test suite
  - Baseline query validation
  - ChromaDB persistence checks
- **Artifacts:** ChromaDB debug dump on failure
- **Duration:** ~15 min (excluding model download)

#### `e2e-tests`
- **Runs:** Full BIRS suite (original tests)
- **Validates:**
  - Results JSON structure
  - All test cases execute
  - Baseline answer generation
  - Context retrieval
- **Duration:** ~20 min

#### `e2e-extended`
- **Runs:** BIRS suite with AEO audit tests
- **Tests:** BIRS-01 through BIRS-06
- **Validates:** Extended test metrics
- **Duration:** ~25 min

---

### 3. Dependency Management (`ci-dependencies.yml`)

**Purpose:** Monitor dependency security, freshness, and compliance

**Triggers:**
- Daily at 4 AM UTC
- Pull requests modifying `requirements.txt`
- Manual dispatch

**Jobs:**

#### `dependency-audit`
- **Tools:** pip-audit, safety
- **Checks:**
  - PyPI vulnerability database
  - Security advisories
  - CVE tracking
- **Reports:** JSON security reports
- **Duration:** ~3 min

#### `dependency-updates`
- **Tools:** pip list
- **Features:**
  - Lists outdated packages
  - Shows current vs. latest versions
  - Top 10 outdated packages in summary
- **Duration:** ~2 min

#### `license-compliance`
- **Tool:** pip-licenses
- **Checks:**
  - License distribution
  - Incompatible licenses (GPL, AGPL, etc.)
  - Unknown licenses
- **Outputs:** JSON and Markdown reports
- **Duration:** ~2 min

#### `dependency-graph`
- **Tool:** pipdeptree
- **Generates:**
  - JSON dependency tree
  - Text tree visualization
  - PNG graph (if GraphViz available)
- **Duration:** ~2 min

---

### 4. Performance Benchmarks (`ci-performance.yml`)

**Purpose:** Track system performance over time

**Triggers:**
- Weekly on Sunday at midnight UTC
- Push to `main` (paths: `src/rag.py`, `src/baseline.py`, `scripts/ingest_documents.py`)
- Manual dispatch (with configurable query count)

**Jobs:**

#### `benchmark-rag`
- **Setup:** Full Ollama + ChromaDB
- **Benchmarks:**
  - Ingestion time
  - Query latency (configurable count, default 10)
  - Average/min/max/P95 latencies
  - Answer length
  - Context retrieval count
- **Outputs:** JSON benchmark results
- **Duration:** ~30 min

#### `benchmark-embeddings`
- **Tests:** Embedding generation performance
- **Sizes:** Short, medium, long text
- **Metrics:**
  - Average time per embedding
  - Min/max times
  - Embedding dimensions
- **Duration:** ~3 min

#### `benchmark-chromadb`
- **Operations:**
  - Add 100 documents
  - Single query
  - Batch queries (10x)
  - Get by ID
- **Metrics:** Latency for each operation
- **Duration:** ~2 min

#### `benchmark-history`
- **Only on `main` branch**
- **Stores:** Timestamped benchmark results
- **Commits:** Results to `.benchmark-history/`
- **Duration:** ~1 min

---

### 5. Documentation (`ci-docs.yml`)

**Purpose:** Maintain high-quality, up-to-date documentation

**Triggers:**
- Push to: `main`, `develop` (paths: `src/**/*.py`, `docs/**`, `README.md`)
- Pull requests to: `main`
- Manual dispatch

**Jobs:**

#### `validate-docs`
- **Checks:**
  - Broken markdown links
  - Code example syntax
  - Documentation completeness (docstrings)
- **Scans:** All modules, classes, functions
- **Duration:** ~2 min

#### `generate-api-docs`
- **Tools:** pdoc3, custom generator
- **Generates:**
  - HTML API documentation
  - `docs/API_REFERENCE.md`
  - Module reference with docstrings
- **Duration:** ~3 min

#### `check-readme`
- **Validates:**
  - Required sections (Installation, Usage, Requirements, Setup)
  - Code block formatting
  - Unclosed code fences
- **Duration:** ~1 min

#### `update-docs-site`
- **Only on `main` branch**
- **Deploys:** GitHub Pages site
- **Includes:**
  - README
  - All docs/ files
  - Generated API docs
  - Custom index.html
- **Duration:** ~5 min

---

### 6. Code Quality (`ci-quality.yml`)

**Purpose:** Track code health metrics and technical debt

**Triggers:**
- Push to: `main`, `develop`
- Pull requests to: `main`
- Weekly on Monday at 6 AM UTC
- Manual dispatch

**Jobs:**

#### `code-coverage`
- **Tool:** pytest-cov
- **Generates:**
  - JSON, XML, HTML reports
  - Coverage badge JSON
  - Per-file coverage breakdown
- **Features:**
  - PR comment with coverage
  - Overall and file-level metrics
- **Duration:** ~5 min

#### `complexity-analysis`
- **Tools:** radon, xenon, mccabe
- **Measures:**
  - Cyclomatic complexity
  - Complexity ranking (A-F)
  - High complexity warnings (>10)
- **Thresholds:** Max B for modules, A for average
- **Duration:** ~2 min

#### `maintainability-index`
- **Tool:** radon mi
- **Calculates:**
  - Maintainability Index per file
  - Ranking: A (>20), B (10-20), C (<10)
  - Average MI across project
- **Duration:** ~2 min

#### `code-duplication`
- **Tool:** pylint (duplicate-code check)
- **Detects:** Duplicate code blocks
- **Reports:** Top 5 duplications
- **Duration:** ~3 min

#### `tech-debt`
- **Custom analyzer**
- **Tracks:**
  - TODO/FIXME/HACK/WARNING comments
  - Deprecated code markers
  - Long functions (>30 lines)
  - Long lines (>120 chars)
- **Calculates:** Weighted debt score
- **Duration:** ~1 min

#### `quality-summary`
- **Aggregates:** All quality job results
- **Generates:** Unified dashboard in summary
- **Duration:** ~1 min

---

### 7. Nightly Extended Tests (`ci-nightly.yml`)

**Purpose:** Long-running comprehensive tests and multi-model validation

**Triggers:**
- Nightly at 1 AM UTC
- Manual dispatch (with options for DeepEval and multi-model)

**Jobs:**

#### `extended-aeo-tests`
- **Timeout:** 60 minutes
- **Runs:** Full BIRS suite with all extended tests
- **Features:**
  - All 6 BIRS test cases
  - AEO audit metrics
  - Regression detection
- **Checks:** Minimum acceptable scores per test
- **Duration:** ~30 min

#### `multi-model-comparison`
- **Only if:** Manual dispatch with `run_multi_model=true`
- **Models:** Llama 3.2, Mistral, Phi3
- **Tests:** Each model against full suite
- **Outputs:** Comparison table with scores
- **Duration:** ~60 min

#### `deepeval-metrics`
- **Only if:** Manual dispatch with `run_deepeval=true`
- **Requires:** `DEEPEVAL_API_KEY` secret
- **Runs:** BIRS with DeepEval bias/hallucination metrics
- **Duration:** ~30 min

#### `create-issue-on-failure`
- **Only on:** Scheduled runs
- **Triggers:** If any test job fails
- **Creates:** GitHub issue with failure details
- **Labels:** `automated-test`, `nightly-failure`, `needs-investigation`

---

### 8. Crawler Test (`crawler-test.yml`)

**Purpose:** Validate web crawler functionality

**Triggers:**
- Weekly on Monday at 3 AM UTC
- Manual dispatch (with brand and max-docs inputs)

**Jobs:**

#### `test-crawler`
- **Tests:** Basic crawler with default brand
- **Configurable:** Brand name, max documents
- **Validates:** Document count, JSON structure
- **Duration:** ~10 min

#### `test-crawler-with-config`
- **Tests:** Crawler with seed URLs config file
- **Uses:** `seed_urls.example.json`
- **Duration:** ~10 min

#### `test-crawler-sentiment-filter`
- **Tests:** Sentiment filtering functionality
- **Validates:** Negative content exclusion
- **Duration:** ~10 min

---

### 9. Release (`release.yml`)

**Purpose:** Validate and publish releases

**Triggers:**
- Push tag: `v*.*.*` (e.g., v1.0.0)
- Manual dispatch (with version input)

**Jobs:**

#### `validate-release`
- **Runs:** All unit tests
- **Validates:** Version consistency
- **Duration:** ~5 min

#### `build-release`
- **Creates:** Python distribution packages
- **Generates:** Wheel and source distribution
- **Uploads:** Distribution artifacts
- **Duration:** ~3 min

#### `create-release`
- **Generates:** Release notes from commits
- **Creates:** GitHub Release
- **Attaches:** Distribution packages
- **Duration:** ~2 min

---

## Secrets Required

| Secret | Required For | Description |
|--------|-------------|-------------|
| `DEEPEVAL_API_KEY` | ci-nightly.yml (optional) | DeepEval cloud judge API key |
| `CODECOV_TOKEN` | ci-tests-sharded.yml (optional) | Codecov upload token |
| `GITHUB_TOKEN` | All workflows | Auto-provided by GitHub Actions |

---

## Artifact Retention

| Artifact | Retention | Size |
|----------|-----------|------|
| Code coverage reports | 90 days | ~5 MB |
| Benchmark results | 90 days | ~500 KB |
| Security reports | 90 days | ~100 KB |
| API documentation | 90 days | ~10 MB |
| Test failure logs | 30 days | ~1 MB |

---

## Performance Considerations

### Caching Strategy
- **pip cache:** Used in all workflows for faster dependency installation
- **Ollama models:** Downloaded once per workflow run (not cached between runs)
- **ChromaDB:** Regenerated per test run for consistency

### Parallel Execution
- Unit tests: Run in parallel with pytest-xdist
- Matrix builds: Python 3.10, 3.11, 3.12 run concurrently
- Independent jobs run in parallel where possible

### Optimization Tips
1. **Branch protection:** Require only critical workflows (ci-tests, ci-integration) for PR merge
2. **Skip long tests:** Use `[skip ci]` in commit message for documentation-only changes
3. **Manual dispatch:** Use for expensive operations (multi-model, DeepEval)
4. **Scheduled frequency:** Adjust cron schedules based on change frequency

---

## Monitoring and Alerts

### GitHub Actions Dashboard
- View workflow runs: `.github/workflows` tab
- Monitor success rates and durations
- Review artifact downloads

### Automated Alerts
- **Nightly test failures:** Auto-creates GitHub issue
- **Security vulnerabilities:** Daily dependency audit
- **Performance regressions:** Weekly benchmarks with history

### Recommended Monitoring
1. Set up GitHub Actions status checks for required workflows
2. Enable email notifications for failed scheduled workflows
3. Review quality metrics weekly
4. Track benchmark trends monthly

---

## Troubleshooting

### Common Issues

#### Ollama Installation Timeout
**Symptom:** Workflow times out during model download
**Solution:** Increase timeout or use pre-cached runner

#### ChromaDB Persistence Issues
**Symptom:** E2E tests fail with empty collections
**Solution:** Check ingestion logs, verify documents.json exists

#### Coverage Upload Failures
**Symptom:** Codecov upload step fails
**Solution:** Verify `CODECOV_TOKEN` secret is set

#### Multi-Model Tests Exceed Limits
**Symptom:** Workflow cancelled due to 6-hour limit
**Solution:** Reduce number of models or test iterations

### Debug Tips
1. Enable debug logging: Set `ACTIONS_STEP_DEBUG` secret to `true`
2. Download artifacts for detailed logs
3. Use manual dispatch to test specific scenarios
4. Check job summaries for inline metrics

---

## Extending the Pipeline

### Adding a New Workflow
1. Create `.github/workflows/ci-newfeature.yml`
2. Define trigger conditions (push, PR, schedule)
3. Add jobs with clear names and purposes
4. Use artifacts for important outputs
5. Update this documentation

### Adding a New Test Suite
1. Create test file in `tests/`
2. Use pytest markers: `@pytest.mark.integration`, `@pytest.mark.e2e`
3. Add to appropriate CI workflow
4. Update test documentation

### Adding New Dependencies
1. Add to `requirements.txt`
2. Triggers `ci-dependencies.yml` automatically
3. Review security scan results
4. Update documentation if needed

---

## Best Practices

### Workflow Design
- ✅ Keep jobs focused and single-purpose
- ✅ Use matrix builds for multiple versions
- ✅ Cache dependencies when possible
- ✅ Set reasonable timeouts
- ✅ Upload artifacts for debugging
- ✅ Use clear job and step names

### Testing Strategy
- ✅ Fast unit tests in all PRs
- ✅ Integration tests on main/develop
- ✅ Extended tests nightly
- ✅ Performance tests weekly
- ✅ Manual dispatch for expensive operations

### Maintenance
- ✅ Review failed scheduled workflows within 24 hours
- ✅ Update dependencies monthly
- ✅ Clean up old artifacts quarterly
- ✅ Review and update thresholds quarterly
- ✅ Keep documentation synchronized with code

---

## CI/CD Metrics

### Success Metrics
- **Build success rate:** Target >95% on main
- **Average build time:** Target <15 min for PR builds
- **Test coverage:** Target >80%
- **Mean time to recovery:** Target <2 hours

### Quality Gates
- **Required for merge:**
  - Lint checks pass
  - Unit tests pass (all Python versions)
  - Code coverage >70%
  - Security scan passes
  
- **Recommended for release:**
  - Integration tests pass
  - Performance benchmarks within 10% of baseline
  - Documentation complete
  - Zero high-severity security issues

---

## Resources

### GitHub Actions Documentation
- [Workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Environment variables](https://docs.github.com/en/actions/learn-github-actions/environment-variables)
- [Artifacts and caching](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)

### Tool Documentation
- [pytest](https://docs.pytest.org/)
- [Black](https://black.readthedocs.io/)
- [Radon](https://radon.readthedocs.io/)
- [Ollama](https://ollama.ai/docs)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2024-01-XX | Initial CI/CD pipeline implementation | GitHub Copilot |
| 2024-01-XX | Added performance benchmarking workflow | GitHub Copilot |
| 2024-01-XX | Added code quality metrics workflow | GitHub Copilot |
| 2024-01-XX | Added nightly extended tests | GitHub Copilot |

---

*Last updated: 2024-01-XX*
*Pipeline version: 1.0.0*
