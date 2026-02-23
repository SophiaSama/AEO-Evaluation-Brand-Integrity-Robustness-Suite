# 🚀 CI/CD Quick Wins Implementation Guide

**Goal:** Implement the highest-impact CI/CD improvements in ~1 hour  
**Expected Result:** 50-60% reduction in CI execution time

---

## Priority 1: Cache Ollama Models (30 min saved per run)

### Implementation

Edit `.github/workflows/ci-integration.yml`:

```yaml
# Add after "Start Ollama service" step
- name: Cache Ollama models
  uses: actions/cache@v4
  with:
    path: ~/.ollama/models
    key: ollama-llama3.2-${{ runner.os }}-v1
    restore-keys: |
      ollama-llama3.2-${{ runner.os }}-
      ollama-

- name: Pull Llama 3.2 model
  run: |
    # Check if model exists
    if ollama list | grep -q llama3.2; then
      echo "✓ Model already cached"
    else
      echo "Pulling model..."
      ollama pull llama3.2
    fi
  timeout-minutes: 5  # Much faster with cache
```

Apply same pattern to:
- `.github/workflows/ci-nightly.yml`
- `.github/workflows/ci-performance.yml`

**Expected Impact:** 
- First run: 30 minutes (unchanged)
- Subsequent runs: ~1 minute (29 minutes saved)
- Cache hit rate: ~90%

---

## Priority 2: Cache Embedding Models (5 min saved per run)

### Implementation

Add to all workflows that run tests:

```yaml
# Add after Python setup
- name: Cache HuggingFace models
  uses: actions/cache@v4
  with:
    path: ~/.cache/huggingface
    key: embeddings-all-MiniLM-L6-v2-${{ runner.os }}
    restore-keys: |
      embeddings-all-MiniLM-L6-v2-
```

Apply to:
- `.github/workflows/ci-integration.yml`
- `.github/workflows/ci-nightly.yml`
- `.github/workflows/ci-performance.yml`

**Expected Impact:** 
- First download: ~80MB, ~2-5 minutes
- Cached: instant
- Savings: 5 minutes per run

---

## Priority 3: Parallel Jobs in ci-tests-sharded.yml (5 min saved)

### Implementation

Edit `.github/workflows/ci-tests-sharded.yml`:

```yaml
# BEFORE:
jobs:
  lint:
    ...
  unit-tests-sharded:
    needs: lint  # ❌ Sequential

# AFTER:
jobs:
  lint:
    ...
  unit-tests-sharded:
    # ✅ Parallel - remove "needs: lint"
```

**Rationale:** Linting and tests can run simultaneously. If lint fails, the PR will still show failure.

**Expected Impact:**
- Before: lint (3 min) → tests (7 min) = 10 minutes
- After: max(lint, tests) = 7 minutes
- Savings: 3 minutes per run

---

## Priority 4: Upload HTML Visualization Artifacts

### Implementation

Add to `.github/workflows/ci-integration.yml`:

```yaml
# Add after "Run full BIRS suite" step
- name: Upload HTML visualization reports
  if: always()  # Upload even if tests fail
  uses: actions/upload-artifact@v4
  with:
    name: birs-html-reports-${{ github.run_number }}
    path: |
      results/*.html
      results/model_comparison/*.html
    retention-days: 30

- name: Comment PR with report link
  if: github.event_name == 'pull_request' && always()
  uses: actions/github-script@v7
  with:
    script: |
      const runId = context.runId;
      const repo = context.repo.owner + '/' + context.repo.repo;
      const artifactUrl = `https://github.com/${repo}/actions/runs/${runId}`;
      
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: `📊 **Interactive Test Reports Generated**\n\n[View artifacts](${artifactUrl}) - Download \`birs-html-reports\` and open \`birs_results.html\` in your browser.`
      });
```

**Expected Impact:**
- Better visibility of test results
- Easier debugging
- Professional reporting

---

## Priority 5: Multi-Model Matrix Testing

### Implementation

Add new job to `.github/workflows/ci-nightly.yml`:

```yaml
multi-model-matrix:
  name: Test Model - ${{ matrix.model }}
  runs-on: ubuntu-latest
  if: github.event.inputs.run_multi_model == 'true' || github.event_name == 'schedule'
  strategy:
    fail-fast: false
    matrix:
      model: [llama3.2, mistral, phi3]
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Cache Ollama models
      uses: actions/cache@v4
      with:
        path: ~/.ollama/models
        key: ollama-${{ matrix.model }}-${{ runner.os }}
    
    - name: Cache HuggingFace models
      uses: actions/cache@v4
      with:
        path: ~/.cache/huggingface
        key: embeddings-${{ runner.os }}
    
    - name: Install Ollama
      run: curl -fsSL https://ollama.com/install.sh | sh
    
    - name: Start Ollama
      run: |
        ollama serve &
        sleep 5
        ollama pull ${{ matrix.model }}
      timeout-minutes: 5
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run BIRS with ${{ matrix.model }}
      env:
        OLLAMA_MODEL: ${{ matrix.model }}
      run: python -m src.run_suite
    
    - name: Upload results
      uses: actions/upload-artifact@v4
      with:
        name: results-${{ matrix.model }}
        path: results/
```

**Expected Impact:**
- Before: 3 models × 40 min = 120 minutes sequential
- After: 40 minutes parallel (3x speedup)
- Savings: 80 minutes on multi-model runs

---

## Complete Implementation Checklist

### Step 1: ci-integration.yml
- [ ] Add Ollama model caching (line ~45)
- [ ] Add HuggingFace embedding caching (line ~35)
- [ ] Add HTML artifact upload (line ~150)
- [ ] Add PR comment with report link (line ~160)

### Step 2: ci-tests-sharded.yml
- [ ] Remove `needs: lint` from unit-tests-sharded job (line ~150)
- [ ] Verify matrix testing is enabled

### Step 3: ci-nightly.yml
- [ ] Add Ollama model caching
- [ ] Add multi-model matrix job
- [ ] Update existing multi-model logic to use matrix

### Step 4: ci-performance.yml
- [ ] Add Ollama model caching
- [ ] Add embedding model caching
- [ ] Add ChromaDB caching (optional)

### Step 5: Test & Verify
- [ ] Create test branch
- [ ] Push changes
- [ ] Monitor Actions run
- [ ] Verify cache creation
- [ ] Verify artifacts uploaded
- [ ] Check execution times

---

## Testing Strategy

### 1. Test Cache Creation (First Run)
```bash
git checkout -b ci/add-caching
# Make changes
git commit -m "Add Ollama and embedding model caching"
git push
```

Watch Actions:
- First run will be slow (creating caches)
- Check "Post Run actions/cache" for cache save confirmation

### 2. Test Cache Hit (Second Run)
```bash
# Make trivial change
echo "# test" >> README.md
git commit -m "Test cache hit"
git push
```

Watch Actions:
- Should see "Cache restored from key: ollama-llama3.2-..."
- Model download should skip or be instant
- Overall time should be 50-60% faster

### 3. Test Parallel Execution
Watch ci-tests workflow:
- lint and unit-tests should start simultaneously
- Total time should equal longest job, not sum

---

## Validation Commands

### Check Cache Status
```bash
# GitHub CLI
gh run view <run-id> --log | grep -i cache

# Expected output:
# Cache restored from key: ollama-llama3.2-Linux-v1
# Cache saved with key: embeddings-all-MiniLM-L6-v2-Linux
```

### Compare Run Times
```bash
# Before optimizations
gh run list --workflow=ci-integration.yml --limit 1 --json durationMs

# After optimizations
gh run list --workflow=ci-integration.yml --limit 1 --json durationMs

# Calculate savings
```

---

## Rollback Plan

If issues arise:

```bash
# Revert changes
git revert HEAD
git push

# Or delete cache via GitHub UI
# Settings → Actions → Caches → Delete specific cache
```

---

## Expected Results Summary

| Workflow | Before | After | Savings |
|----------|--------|-------|---------|
| ci-tests | 15 min | 10 min | 33% |
| ci-integration (first) | 45 min | 45 min | 0% |
| ci-integration (cached) | 45 min | 15 min | 67% |
| ci-nightly (3 models) | 120 min | 40 min | 67% |
| ci-performance (cached) | 30 min | 10 min | 67% |

**Overall: 50-60% reduction in CI time**

---

## Maintenance

### Cache Management
- **TTL**: GitHub caches expire after 7 days of no use
- **Size limit**: 10 GB per repository
- **Monitoring**: Check Settings → Actions → Caches

### When to Invalidate Cache
- Model version changes: Update cache key `v1` → `v2`
- Requirements.txt changes: Automatic with `cache: 'pip'`
- Document changes: Automatic with hash-based keys

### Cleanup Old Caches
```bash
# Via GitHub CLI
gh cache list
gh cache delete <cache-id>

# Or use Actions workflow
- name: Cleanup old caches
  run: gh cache delete --all
  if: github.event_name == 'workflow_dispatch'
```

---

## Next Steps After Quick Wins

1. **Monitor** - Track CI times for 1 week
2. **Measure** - Document actual time savings
3. **Phase 2** - Implement test sharding
4. **Phase 3** - Add visualization CI workflow
5. **Optimize** - Fine-tune cache keys based on hit rates

---

**Ready to implement?** Start with Step 1 (ci-integration.yml) and test before proceeding to others.

**Questions?** Refer to [CI_CD_REVIEW.md](CI_CD_REVIEW.md) for detailed analysis.
