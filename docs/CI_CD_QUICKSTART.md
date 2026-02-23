# CI/CD Quick Start Guide

This guide will help you set up and configure the BIRS CI/CD pipelines for your repository.

## Prerequisites

- GitHub repository with BIRS code
- GitHub Actions enabled (free for public repos, included in GitHub plans)
- Admin access to repository settings
- **No Docker required!** ✅ All workflows run on GitHub-hosted runners

> **Note:** BIRS CI/CD uses native GitHub-hosted Ubuntu VMs, not Docker containers. This provides faster execution, better caching, and simpler configuration. See [Docker Optional Guide](CI_CD_DOCKER_OPTIONAL.md) if you need containerization for specific use cases.

---

## Initial Setup

### 1. Enable GitHub Actions

GitHub Actions should be enabled by default. To verify:

1. Go to your repository on GitHub
2. Click **Settings** → **Actions** → **General**
3. Under "Actions permissions", ensure actions are allowed
4. Under "Workflow permissions", set to **Read and write permissions**

### 2. Configure Branch Protection

Recommended branch protection rules for `main`:

1. Go to **Settings** → **Branches** → **Add rule**
2. Branch name pattern: `main`
3. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
     - Select: `lint`, `unit-tests`, `structure-validation`
   - ✅ Require branches to be up to date before merging
   - ✅ Do not allow bypassing the above settings

### 3. Set Up Secrets (Optional)

Some workflows require secrets for enhanced functionality:

#### Required Secrets: None
All core workflows work without additional secrets.

#### Optional Secrets

| Secret | Purpose | How to Get |
|--------|---------|------------|
| `CODECOV_TOKEN` | Upload coverage to Codecov | Sign up at [codecov.io](https://codecov.io) |
| `DEEPEVAL_API_KEY` | Run DeepEval metrics | Sign up at [deepeval.com](https://deepeval.com) |

**To add secrets:**
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Enter name and value
4. Click **Add secret**

---

## Workflow Configuration

### Adjust Scheduled Workflows

Default schedules:

```yaml
ci-dependencies.yml  : Daily at 4 AM UTC
ci-nightly.yml       : Daily at 1 AM UTC
ci-performance.yml   : Weekly on Sunday at 12 AM UTC
crawler-test.yml     : Weekly on Monday at 3 AM UTC
```

To change schedules:

1. Edit the workflow file in `.github/workflows/`
2. Modify the `cron` expression:

```yaml
on:
  schedule:
    - cron: '0 4 * * *'  # Format: minute hour day month weekday
```

**Cron examples:**
- `0 4 * * *` = Daily at 4 AM UTC
- `0 0 * * 0` = Weekly on Sunday at midnight UTC
- `0 1 * * 1` = Weekly on Monday at 1 AM UTC
- `0 */6 * * *` = Every 6 hours

### Disable Unnecessary Workflows

If you don't need certain workflows:

**Option 1: Disable in GitHub UI**
1. Go to **Actions** tab
2. Select the workflow from the left sidebar
3. Click **⋯** (three dots) → **Disable workflow**

**Option 2: Delete workflow file**
```powershell
# Remove the workflow file
Remove-Item .github\workflows\ci-nightly.yml
git commit -m "Disable nightly extended tests"
git push
```

---

## First Run

### Trigger Initial Workflows

1. **Make a small commit:**
   ```powershell
   # Add a comment to a file
   Add-Content README.md "`n<!-- CI test -->"
   git add README.md
   git commit -m "Test CI pipeline"
   git push
   ```

2. **Watch workflows execute:**
   - Go to **Actions** tab
  - You should see `ci-tests-sharded.yml`, `ci-structure-security.yml`, and `ci-quality.yml` running
   - Click on a workflow to see real-time logs

3. **Check results:**
   - ✅ Green checkmark = passed
   - ❌ Red X = failed
   - 🟡 Yellow dot = in progress

### First-Time Model Download

The first run of `ci-integration.yml` will take ~30 minutes to download Llama 3.2 model. Subsequent runs are faster (~15 min).

---

## Testing Workflows Locally

### Manual Dispatch

Test workflows without pushing code:

1. Go to **Actions** tab
2. Select workflow (e.g., `ci-performance.yml`)
3. Click **Run workflow**
4. Select branch and options
5. Click **Run workflow** button

### Test with Act (Optional)

[Act](https://github.com/nektos/act) runs GitHub Actions locally:

```powershell
# Install Act
winget install nektos.act

# Test a workflow
act -W .github\workflows\ci-tests-sharded.yml
```

Note: Some workflows (like Ollama setup) may not work perfectly with Act.

---

## Monitoring

### GitHub Actions Dashboard

**Main view:**
- Go to **Actions** tab
- See all workflow runs
- Filter by status, event, workflow

**Workflow-specific view:**
- Click workflow name in sidebar
- See run history
- View success rates

### Job Summaries

Each workflow creates a summary with:
- Test results
- Coverage metrics
- Performance benchmarks
- Quality metrics

**To view:**
1. Click on a workflow run
2. Scroll down to **Summary** section

### Artifacts

Download workflow outputs:

1. Click on completed workflow run
2. Scroll to **Artifacts** section
3. Click artifact name to download ZIP

**Available artifacts:**
- Code coverage reports (HTML)
- Benchmark results (JSON)
- Security reports (JSON)
- API documentation (HTML)
- Test failure logs

### Email Notifications

Configure email alerts:

1. Go to **Profile** → **Settings** → **Notifications**
2. Under "Actions", enable:
   - ✅ Send notifications for failed workflows only
   - ✅ Only for workflows triggered by me

---

## Troubleshooting

### Workflow Fails on First Run

**Common causes:**

1. **Ollama timeout:** Model download takes ~30 min first time
   - Solution: Increase timeout in workflow or wait for completion

2. **Missing documents.json:** Required for ingestion
   - Solution: Ensure `data/documents/documents.json` exists

3. **Python version mismatch:** Tests run on 3.10, 3.11, 3.12
   - Solution: Ensure code is compatible with all versions

### Check Workflow Logs

1. Go to **Actions** tab
2. Click failed workflow run
3. Click failed job
4. Expand failed step to see detailed logs

### Re-run Failed Workflows

1. Open failed workflow run
2. Click **Re-run jobs** dropdown
3. Choose **Re-run failed jobs** or **Re-run all jobs**

---

## Customization

### Add Your Own Workflow

Create a new workflow file:

```yaml
# .github/workflows/custom-workflow.yml
name: Custom Workflow

on:
  push:
    branches: [main]

jobs:
  custom-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run custom script
        run: |
          echo "Custom workflow running"
          python scripts/my_script.py
```

### Modify Existing Workflows

Example: Add Slack notifications

```yaml
# Add to any workflow job
- name: Notify Slack
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Adjust Quality Thresholds

**Coverage threshold:**
```yaml
# In ci-quality.yml → code-coverage job
- name: Check coverage threshold
  run: |
    coverage report --fail-under=80  # Fail if < 80%
```

**Complexity threshold:**
```yaml
# In ci-quality.yml → complexity-analysis job
- name: Check complexity thresholds
  run: |
    xenon src/ --max-absolute B --max-modules A  # Adjust grades
```

---

## Best Practices

### Branch Strategy

**Recommended workflow:**
```
feature/new-test → PR → ci-tests + ci-quality
                       ↓ (if pass)
                    develop → ci-integration
                       ↓ (if pass)
                     main → all workflows + deploy
```

### Commit Messages

Use conventional commits to control CI:

```bash
# Skip CI for docs-only changes
git commit -m "docs: update README [skip ci]"

# Trigger specific workflow
git commit -m "perf: optimize RAG query" # Triggers ci-performance.yml
```

### Pull Request Workflow

1. Create feature branch
2. Make changes and commit
3. Push and create PR
4. Wait for required checks (ci-tests, ci-integration)
5. Review coverage and quality reports in PR comments
6. Address any issues
7. Merge when all checks pass

### Release Process

1. Ensure all tests pass on `main`
2. Create and push tag:
   ```powershell
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```
3. `release.yml` triggers automatically
4. GitHub Release created with artifacts

---

## Performance Optimization

### Speed Up Workflows

1. **Use caching:**
   ```yaml
   - uses: actions/setup-python@v5
     with:
       python-version: '3.11'
       cache: 'pip'  # Cache pip dependencies
   ```

2. **Run jobs in parallel:**
   ```yaml
   jobs:
     test-python-310:
       runs-on: ubuntu-latest
     test-python-311:
       runs-on: ubuntu-latest
     # Both run simultaneously
   ```

3. **Skip unnecessary jobs:**
   ```yaml
   jobs:
     docs:
       if: contains(github.event.head_commit.message, '[docs]')
   ```

### Reduce Workflow Runs

1. **Limit paths:**
   ```yaml
   on:
     push:
       paths:
         - 'src/**'
         - 'tests/**'
         # Only trigger when these files change
   ```

2. **Combine workflows:**
   - Merge similar jobs into one workflow
   - Use job dependencies to sequence execution

---

## Security Best Practices

### Protect Secrets

- ✅ Never commit secrets to code
- ✅ Use GitHub Secrets for sensitive data
- ✅ Use environment-specific secrets
- ✅ Rotate secrets regularly

### Limit Permissions

```yaml
permissions:
  contents: read        # Read-only by default
  pull-requests: write  # Only if needed for PR comments
```

### Pin Action Versions

```yaml
# ✅ Good: Pin to specific version
- uses: actions/checkout@v4

# ❌ Bad: Use latest
- uses: actions/checkout@main
```

---

## Getting Help

### Resources

- 📖 [BIRS CI/CD Documentation](CI_CD_PIPELINES.md)
- 🏗️ [Pipeline Architecture](CI_CD_ARCHITECTURE.md)
- 🐙 [GitHub Actions Docs](https://docs.github.com/en/actions)
- 💬 [GitHub Community Forum](https://github.community/)

### Common Issues

See [CI/CD Troubleshooting](CI_CD_PIPELINES.md#troubleshooting) in main documentation.

### Debug Mode

Enable verbose logging:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add repository secret: `ACTIONS_STEP_DEBUG` = `true`
3. Re-run workflow to see detailed logs

---

## Checklist

Use this checklist to ensure proper CI/CD setup:

- [ ] GitHub Actions enabled
- [ ] Branch protection configured for `main`
- [ ] First workflow run completed successfully
- [ ] Secrets added (if using optional features)
- [ ] Email notifications configured
- [ ] Workflow schedules adjusted for your needs
- [ ] Unnecessary workflows disabled
- [ ] Team members have access to view workflows
- [ ] Documentation read and understood

---

*Last updated: 2024-01-XX*
