# BIRS CI/CD FAQ

## Frequently Asked Questions

### Security & Privacy

#### Q: How do I ensure the LLM is only called locally in GitHub Actions?
**A: BIRS has multiple protection layers to guarantee local-only execution:**

1. **Configuration hardcoded to localhost:**
   ```python
   OLLAMA_BASE_URL = "http://localhost:11434"  # Always local
   ```

2. **Only local LLM classes used:**
   ```python
   from langchain_community.chat_models import ChatOllama  # Local
   # NOT ChatOpenAI, ChatAnthropic, etc. (cloud)
   ```

3. **Automatic security verification:**
   Every workflow checks:
   - ✅ Ollama running on localhost
   - ✅ No cloud API keys present
   - ✅ Configuration points to localhost
   - ✅ No cloud LLM imports

4. **Visible in workflow summary:**
   ```
   🔒 Security Verification: Local LLM Only
   ✅ Ollama running on localhost:11434
   ✅ No cloud API keys present
   ✅ Security Guarantee: All LLM inference happens locally
   ```

**See:** [Security Documentation](SECURITY_LOCAL_LLM.md) for complete details.

---

#### Q: Does any data get sent to external APIs?
**A: No! ✅** All data stays on the GitHub Actions runner:
- Ollama runs locally (not a cloud service)
- No API keys for cloud LLMs (OpenAI, Anthropic, etc.)
- Network monitoring can verify no external calls
- Complete audit trail in workflow logs

**Exception:** DeepEval (optional, opt-in, manual only) can use cloud LLMs to evaluate model **outputs** (not poison **inputs**).

---

#### Q: How can I verify no external API calls are made?
**A:** Several ways:

1. **Check workflow logs** - Every run shows security verification
2. **Inspect configuration** - `src/config.py` hardcoded to localhost
3. **Review code** - No cloud LLM imports in `src/rag.py`
4. **Add network monitoring** - See [Security Guide](SECURITY_LOCAL_LLM.md)

---

#### Q: What about DeepEval? Doesn't it use cloud APIs?
**A:** DeepEval is **optional and isolated:**
- ❌ NOT used in standard CI/CD pipeline
- ❌ NOT enabled by default
- ✅ Only runs with manual dispatch + explicit flag
- ✅ Only evaluates model outputs, NOT poison inputs
- ✅ Requires explicit `DEEPEVAL_API_KEY` secret

You have complete control over whether it runs.

---

### Infrastructure & Setup

#### Q: Do I need Docker to run the CI/CD pipelines?
**A: No! ✅** All BIRS workflows run on GitHub-hosted Ubuntu virtual machines without Docker. The workflows use native Python, pip, and system tools which are:
- Faster (no image pulling)
- Simpler (less configuration)
- Better cached (pip cache works natively)
- Free (included with GitHub Actions)

See [Docker Optional Guide](CI_CD_DOCKER_OPTIONAL.md) if you specifically need Docker for other reasons.

---

#### Q: What infrastructure do I need to set up?
**A: Nothing!** GitHub provides everything:
- Ubuntu VM with pre-installed tools
- Python 3.10, 3.11, 3.12
- Git, curl, pip, and common build tools
- Free minutes for public repos

Just enable GitHub Actions in your repository settings.

---

#### Q: How much does this cost?
**A:** 
- **Public repositories:** Free unlimited minutes ✅
- **Private repositories:** 
  - Free tier: 2,000 minutes/month
  - Team: 3,000 minutes/month
  - Enterprise: 50,000 minutes/month

BIRS daily scheduled workflows use ~2 hours/day = ~60 hours/month = ~3,600 minutes/month.

**Cost optimization:**
- Disable expensive workflows (multi-model, nightly)
- Reduce scheduled frequency
- Use manual dispatch instead of schedules

---

#### Q: Can I run the workflows locally?
**A: Yes, with limitations:**

1. **Run tests directly:**
   ```powershell
   python -m pytest tests/ -v
   python -m pytest tests/ -m "not integration and not e2e"
   ```

2. **Use Act (GitHub Actions emulator):**
   ```powershell
   winget install nektos.act
  act -W .github\workflows\ci-tests-sharded.yml
   ```
   
   Note: Ollama and ChromaDB workflows may not work perfectly with Act.

3. **Run scripts manually:**
   ```powershell
   python scripts/ingest_documents.py
   python -m pytest tests/ --cov=src
   black --check src/
   flake8 src/
   ```

---

### Secrets & Configuration

#### Q: What secrets are required?
**A: None!** All core workflows work without additional configuration.

**Optional secrets:**
- `CODECOV_TOKEN` - For coverage tracking (optional)
- `DEEPEVAL_API_KEY` - For DeepEval metrics (optional)
- `GITHUB_TOKEN` - Auto-provided by GitHub (don't add manually)

---

#### Q: How do I add a secret?
**A:**
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Enter name (e.g., `CODECOV_TOKEN`)
4. Enter value
5. Click **Add secret**

---

#### Q: Can I use environment-specific configurations?
**A: Yes!** Use GitHub Environments:

1. Go to **Settings** → **Environments**
2. Create environments (e.g., `staging`, `production`)
3. Add environment-specific secrets
4. Reference in workflows:

```yaml
jobs:
  deploy:
    environment: production
    steps:
      - run: echo "Using production config"
```

---

### Workflows & Execution

#### Q: Which workflows run on every push?
**A:** On push to `main`/`develop` or PR:
- ✅ `ci-tests-sharded.yml` (~10 min)
- ✅ `ci-structure-security.yml` (~4 min)
- ✅ `ci-quality.yml` (~20 min)
- ✅ `ci-docs.yml` (~10 min)
- ✅ `ci-integration.yml` (~30 min, only on push to main/develop)

**Total PR check time:** ~40 minutes (tests, quality, docs run in parallel)

---

#### Q: How do I run a workflow manually?
**A:**
1. Go to **Actions** tab
2. Select workflow from left sidebar
3. Click **Run workflow** button
4. Select branch
5. Fill in any input parameters
6. Click **Run workflow**

---

#### Q: How do I skip CI on a commit?
**A:** Add `[skip ci]` or `[ci skip]` to your commit message:

```powershell
git commit -m "docs: update README [skip ci]"
```

This skips all workflows on that commit.

---

#### Q: Why is the first integration test run so slow?
**A:** The first run downloads the Llama 3.2 model (~7GB) which takes ~30 minutes. Subsequent runs are much faster (~15 min) because:
- Ollama installs quickly
- Model is cached (per workflow run)
- ChromaDB ingestion is fast

Note: Models are NOT cached between workflow runs, only within a single run.

---

#### Q: Can I cancel a running workflow?
**A: Yes!**
1. Go to **Actions** tab
2. Click on the running workflow
3. Click **Cancel workflow** button (top right)

---

### Failures & Debugging

#### Q: What do I do if a workflow fails?
**A:**
1. Click on the failed workflow run
2. Click on the failed job (red X)
3. Expand the failed step to see error logs
4. Common issues:
   - Test failures → Check test output
   - Linting errors → Run `black src/` locally
   - Timeout → Increase timeout or optimize code
   - Model download → Re-run (network issue)

---

#### Q: How do I see detailed logs?
**A:** Enable debug mode:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add repository secret: `ACTIONS_STEP_DEBUG` = `true`
3. Re-run the workflow
4. Logs will be much more verbose

---

#### Q: How do I re-run a failed workflow?
**A:**
1. Open the failed workflow run
2. Click **Re-run jobs** dropdown (top right)
3. Choose:
   - **Re-run failed jobs** - Only re-runs failed jobs
   - **Re-run all jobs** - Re-runs everything

---

#### Q: Why did my scheduled workflow not run?
**A:** Common reasons:
1. **Repository inactive** - GitHub disables scheduled workflows after 60 days of no activity
2. **Workflow disabled** - Check if it's disabled in Actions settings
3. **GitHub outage** - Check [githubstatus.com](https://githubstatus.com)
4. **Cron syntax error** - Verify cron expression

To re-enable inactive workflows:
- Make any commit to the repository, or
- Manually trigger the workflow

---

### Artifacts & Reports

#### Q: Where can I find test reports?
**A:** After a workflow completes:
1. Go to the workflow run
2. Scroll to **Artifacts** section at bottom
3. Download the ZIP files:
   - `code-coverage-report` - HTML coverage report
   - `rag-benchmark-results` - Performance data
   - `security-reports` - Vulnerability scans
   - `api-documentation` - Generated docs

Artifacts expire after 90 days (default).

---

#### Q: How do I view code coverage?
**A:** Three options:

1. **In PR comments** - Automatic comment on PRs with coverage stats
2. **Download artifact** - `code-coverage-report` contains HTML report
3. **Codecov** - If `CODECOV_TOKEN` is set, view at codecov.io

---

#### Q: Where are the benchmark results stored?
**A:** 
- **Immediate:** Artifacts in workflow run
- **History:** Committed to `.benchmark-history/` directory (on main branch only)
- **Trends:** Check `.benchmark-history/` for timestamped results

---

### Customization

#### Q: How do I change the Python version?
**A:** Edit the workflow file:

```yaml
# Single version
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'  # Change here

# Matrix (multiple versions)
strategy:
  matrix:
    python-version: ['3.11', '3.12']  # Modify list
```

---

#### Q: How do I change the schedule?
**A:** Edit the cron expression in the workflow:

```yaml
on:
  schedule:
    - cron: '0 4 * * *'  # Daily at 4 AM UTC
    # Change to: '0 0 * * 0'  # Weekly on Sunday
```

**Cron helper:** [crontab.guru](https://crontab.guru)

---

#### Q: How do I add a new test to CI?
**A:**
1. Create test file in `tests/` directory
2. Add pytest markers if needed:
   ```python
   @pytest.mark.integration
   def test_my_feature():
       ...
   ```
3. Tests automatically run in appropriate workflows:
  - Unit tests: `ci-tests-sharded.yml`
   - Integration tests: `ci-integration.yml`
   - Extended tests: `ci-nightly.yml`

---

#### Q: How do I add a new quality check?
**A:** Edit `ci-quality.yml` and add a new step:

```yaml
- name: Check for console.log
  run: |
    if grep -r "print(" src/; then
      echo "Found print statements"
      exit 1
    fi
```

---

#### Q: Can I add Slack notifications?
**A: Yes!** Add to any workflow:

```yaml
- name: Notify Slack
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

### Performance & Optimization

#### Q: How can I speed up the workflows?
**A:**
1. **Use caching** (already enabled for pip)
2. **Run tests in parallel** (already enabled with pytest-xdist)
3. **Skip unnecessary jobs:**
   ```yaml
   if: contains(github.event.head_commit.message, '[docs]')
   ```
4. **Reduce scheduled frequency**
5. **Use concurrency groups:**
   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.ref }}
     cancel-in-progress: true
   ```

---

#### Q: Why is ChromaDB so slow?
**A:** ChromaDB runs in embedded mode (in-process) which is:
- Slower than server mode
- But simpler for CI (no service setup)
- No network overhead

To optimize:
- Reduce document count for tests
- Use smaller test datasets
- Consider mocking ChromaDB for unit tests

---

#### Q: Can I use self-hosted runners?
**A: Yes!** Self-hosted runners can be faster for:
- Ollama model caching (persistent disk)
- Local ChromaDB
- GPU acceleration

Setup:
1. Go to **Settings** → **Actions** → **Runners**
2. Click **New self-hosted runner**
3. Follow setup instructions
4. Update workflows: `runs-on: self-hosted`

Note: Requires maintaining your own infrastructure.

---

### Branch Protection & Merging

#### Q: Which checks are required to merge a PR?
**A:** Recommended required checks:
- ✅ `lint`
- ✅ `unit-tests` (at least one Python version)
- ✅ `structure-validation`
- ✅ `security-scan`

Optional (slower but more thorough):
- ⚠️ `integration-tests`
- ⚠️ `e2e-tests`

Configure in **Settings** → **Branches** → Branch protection rules.

---

#### Q: Can I merge without waiting for all checks?
**A:** If you're an admin and haven't enforced rules:
- **Yes** - But not recommended
- **Best practice** - Wait for required checks

If you've enabled "Do not allow bypassing the above settings":
- **No** - Must wait for checks (recommended)

---

### Monitoring & Maintenance

#### Q: How do I monitor workflow success rates?
**A:**
1. Go to **Actions** tab
2. Click on a workflow name
3. View run history and success rate
4. Check **Insights** → **Actions** for detailed analytics

---

#### Q: What maintenance is required?
**A:**
- **Daily:** Review failed scheduled workflows
- **Weekly:** Check security scan results
- **Monthly:** Review and update dependencies
- **Quarterly:** Review quality metrics and thresholds

See [CI/CD Checklist](CI_CD_CHECKLIST.md) for detailed maintenance tasks.

---

#### Q: How do I know if a scheduled workflow failed?
**A:** Three ways:
1. **Email notifications** - Configure in GitHub profile settings
2. **Auto-created issues** - `ci-nightly.yml` creates issues on failure
3. **Manual check** - Visit Actions tab periodically

---

### Advanced Topics

#### Q: Can I test multiple databases?
**A: Yes!** Use service containers:

```yaml
services:
  postgres:
    image: postgres:14
  mongodb:
    image: mongo:6
```

See [Docker Optional Guide](CI_CD_DOCKER_OPTIONAL.md) for examples.

---

#### Q: Can I deploy automatically after tests pass?
**A: Yes!** Add a deploy job:

```yaml
jobs:
  deploy:
    needs: [test, integration]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Your deploy commands here
```

---

#### Q: Can I run workflows on a different OS?
**A: Yes!** GitHub provides:
- `ubuntu-latest` (Linux, default)
- `windows-latest` (Windows)
- `macos-latest` (macOS)

Change `runs-on` in workflow file.

---

#### Q: How do I add code scanning for vulnerabilities?
**A:** GitHub has built-in CodeQL:

1. Go to **Security** → **Code scanning**
2. Click **Set up this workflow**
3. Commit the `.github/workflows/codeql.yml` file

Or use Bandit (already included in `ci-structure-security.yml`).

---

## Still Have Questions?

### Resources
- 📖 [CI/CD Pipeline Guide](CI_CD_PIPELINES.md)
- 🏗️ [Pipeline Architecture](CI_CD_ARCHITECTURE.md)
- 🚀 [Quick Start Guide](CI_CD_QUICKSTART.md)
- 🐳 [Docker Optional Guide](CI_CD_DOCKER_OPTIONAL.md)
- ✅ [Setup Checklist](CI_CD_CHECKLIST.md)

### GitHub Documentation
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Community](https://github.community/)

### Get Help
- Check workflow logs for detailed error messages
- Enable debug mode for verbose output
- Review GitHub's troubleshooting guide
- Ask in GitHub Discussions

---

*Last updated: February 6, 2026*
*FAQ version: 1.0*
