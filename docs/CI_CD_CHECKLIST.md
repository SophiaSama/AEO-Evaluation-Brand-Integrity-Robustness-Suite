# BIRS CI/CD Setup Checklist

Use this checklist to ensure your CI/CD pipeline is properly configured and running.

## ✅ Phase 1: Initial Verification (5 minutes)

### GitHub Repository Setup
- [ ] GitHub Actions is enabled in repository settings
- [ ] Workflow files exist in `.github/workflows/` directory
- [ ] All workflow files are present:
  - [ ] `ci-tests-sharded.yml`
  - [ ] `ci-structure-security.yml`
  - [ ] `ci-integration.yml`
  - [ ] `ci-dependencies.yml`
  - [ ] `ci-performance.yml`
  - [ ] `ci-docs.yml`
  - [ ] `ci-quality.yml`
  - [ ] `ci-nightly.yml`
  - [ ] `crawler-test.yml`
  - [ ] `release.yml`

### Documentation
- [ ] Read `docs/CI_CD_QUICKSTART.md`
- [ ] Reviewed `docs/CI_CD_PIPELINES.md`
- [ ] Viewed `docs/CI_CD_ARCHITECTURE.md`
- [ ] Checked `docs/CI_CD_IMPLEMENTATION_SUMMARY.md`

---

## ✅ Phase 2: GitHub Configuration (10 minutes)

### Actions Permissions
- [ ] Go to **Settings** → **Actions** → **General**
- [ ] Verify "Allow all actions and reusable workflows" is selected
- [ ] Set "Workflow permissions" to **Read and write permissions**
- [ ] Enable "Allow GitHub Actions to create and approve pull requests"

### Branch Protection (Optional but Recommended)
- [ ] Go to **Settings** → **Branches**
- [ ] Add rule for `main` branch
- [ ] Enable "Require a pull request before merging"
- [ ] Enable "Require status checks to pass before merging"
- [ ] Select required status checks:
  - [ ] `lint`
  - [ ] `unit-tests-sharded` (all shards)
  - [ ] `structure-validation`
- [ ] Enable "Require branches to be up to date before merging"

### GitHub Pages (Optional)
- [ ] Go to **Settings** → **Pages**
- [ ] Source: **Deploy from a branch**
- [ ] Branch: `main` / `docs-site`
- [ ] Save settings
- [ ] Note your GitHub Pages URL

---

## ✅ Phase 3: Secrets Configuration (5 minutes)

### Required Secrets (None!)
✅ All core workflows work without additional secrets

### Optional Secrets
- [ ] **Codecov** (for coverage tracking):
  - [ ] Sign up at [codecov.io](https://codecov.io)
  - [ ] Get your upload token
  - [ ] Add as `CODECOV_TOKEN` secret
  - [ ] Go to **Settings** → **Secrets and variables** → **Actions**
  - [ ] Click **New repository secret**

- [ ] **DeepEval** (for extended metrics):
  - [ ] Sign up at [deepeval.com](https://deepeval.com)
  - [ ] Get your API key
  - [ ] Add as `DEEPEVAL_API_KEY` secret

---

## ✅ Phase 4: First Test Run (15 minutes)

### Trigger CI Tests
- [ ] Make a small change to trigger workflows:
  ```powershell
  # Add a comment to README
  Add-Content README.md "`n<!-- CI pipeline test -->"
  git add README.md
  git commit -m "test: trigger CI pipeline"
  git push
  ```

### Monitor First Run
- [ ] Go to **Actions** tab
- [ ] Wait for workflows to start
- [ ] Click on running workflow to view logs
- [ ] Workflows that should run automatically:
  - [ ] `ci-tests-sharded.yml` (~10 min)
  - [ ] `ci-structure-security.yml` (~4 min)
  - [ ] `ci-quality.yml` (~20 min)
  - [ ] `ci-docs.yml` (~10 min)

### Verify Success
- [ ] All jobs show green checkmarks ✅
- [ ] Review job summaries (click workflow → summary section)
- [ ] Check artifacts (scroll down in workflow run)
- [ ] View coverage report if uploaded

---

## ✅ Phase 5: Integration Test (30 minutes)

### Trigger Integration Workflow
- [ ] Push to `main` or `develop` branch, OR
- [ ] Manually trigger `ci-integration.yml`:
  - [ ] Go to **Actions** → **BIRS Integration Tests**
  - [ ] Click **Run workflow**
  - [ ] Select branch
  - [ ] Click **Run workflow** button

### Monitor Integration Run
- [ ] Watch Ollama installation (~2 min)
- [ ] Watch Llama 3.2 download (~30 min first time)
- [ ] Watch ingestion process (~3 min)
- [ ] Watch integration tests (~5 min)
- [ ] Watch E2E tests (~10 min each)

### Verify Integration Success
- [ ] `integration-tests` job passes ✅
- [ ] `e2e-tests` job passes ✅
- [ ] `e2e-extended` job passes ✅
- [ ] ChromaDB artifact available (if failed)

---

## ✅ Phase 6: Scheduled Workflows (Optional)

### Verify Scheduled Workflows Will Run
- [ ] Check workflow schedules in GitHub Actions
- [ ] Workflows will auto-run:
  - [ ] `ci-dependencies.yml` - Daily at 4 AM UTC
  - [ ] `ci-nightly.yml` - Daily at 1 AM UTC
  - [ ] `ci-performance.yml` - Weekly Sunday at 12 AM UTC
  - [ ] `crawler-test.yml` - Weekly Monday at 3 AM UTC

### Test Scheduled Workflows Manually (Optional)
- [ ] **Test Dependencies:**
  - [ ] Go to **Actions** → **BIRS Dependency Management**
  - [ ] Click **Run workflow**
  - [ ] Wait ~15 min
  - [ ] Review security reports

- [ ] **Test Performance:**
  - [ ] Go to **Actions** → **BIRS Performance Benchmarks**
  - [ ] Click **Run workflow**
  - [ ] Set `num_queries` to `5` (faster)
  - [ ] Wait ~30 min
  - [ ] Review benchmark results

- [ ] **Test Nightly:**
  - [ ] Go to **Actions** → **BIRS Nightly Extended Tests**
  - [ ] Click **Run workflow**
  - [ ] Leave options unchecked (faster)
  - [ ] Wait ~60 min
  - [ ] Review extended test results

---

## ✅ Phase 7: Monitoring Setup (10 minutes)

### Enable Notifications
- [ ] Go to **Profile** → **Settings** → **Notifications**
- [ ] Under **Actions**, enable:
  - [ ] "Send notifications for failed workflows only"
  - [ ] "Only for workflows triggered by me" (or all)
- [ ] Choose notification method (Email, Web, Mobile)

### Set Up Issue Alerts
- [ ] Verify `ci-nightly.yml` will create issues on failure
- [ ] Check **Issues** tab periodically for auto-created issues
- [ ] Add yourself as watcher for workflow issues

### Review Artifacts Policy
- [ ] Go to **Settings** → **Actions** → **General**
- [ ] Scroll to "Artifact and log retention"
- [ ] Default: 90 days (adjust if needed)

---

## ✅ Phase 8: Quality Gates (5 minutes)

### Configure Status Checks
- [ ] Go to **Settings** → **Branches** → `main` rule
- [ ] Under "Require status checks", add:
  - [ ] `lint`
  - [ ] `unit-tests`
  - [ ] `security-scan`
  - [ ] `structure-validation`
- [ ] Optional (slower):
  - [ ] `integration-tests`
  - [ ] `e2e-tests`

### Test PR Workflow
- [ ] Create a feature branch
- [ ] Make a small change
- [ ] Open a pull request
- [ ] Verify CI checks run automatically
- [ ] Check for coverage comment on PR
- [ ] Verify merge is blocked until checks pass

---

## ✅ Phase 9: Documentation Site (10 minutes)

### Verify GitHub Pages Deployment
- [ ] Push to `main` branch to trigger docs build
- [ ] Go to **Actions** → **BIRS Documentation**
- [ ] Wait for `update-docs-site` job to complete
- [ ] Visit your GitHub Pages URL
- [ ] Verify documentation site loads
- [ ] Check navigation and links work

### Bookmark Key URLs
- [ ] Repository Actions: `https://github.com/<user>/<repo>/actions`
- [ ] GitHub Pages: `https://<user>.github.io/<repo>/`
- [ ] Codecov (if enabled): `https://codecov.io/gh/<user>/<repo>`

---

## ✅ Phase 10: Advanced Features (Optional)

### Test Release Process
- [ ] Create a test tag locally:
  ```powershell
  git tag -a v0.1.0-test -m "Test release"
  git push origin v0.1.0-test
  ```
- [ ] Watch `release.yml` workflow run
- [ ] Verify GitHub Release is created
- [ ] Download and test artifacts
- [ ] Delete test release if successful

### Test Multi-Model Comparison (Expensive)
- [ ] Go to **Actions** → **BIRS Nightly Extended Tests**
- [ ] Click **Run workflow**
- [ ] Enable `run_multi_model`
- [ ] Wait ~90 min
- [ ] Review model comparison results

### Test DeepEval Metrics (Requires API Key)
- [ ] Add `DEEPEVAL_API_KEY` secret
- [ ] Go to **Actions** → **BIRS Nightly Extended Tests**
- [ ] Click **Run workflow**
- [ ] Enable `run_deepeval`
- [ ] Wait ~30 min
- [ ] Review DeepEval metrics

---

## ✅ Phase 11: Customization (Optional)

### Adjust Schedules
- [ ] Review workflow schedules in `.github/workflows/`
- [ ] Modify cron expressions if needed:
  - [ ] `ci-dependencies.yml` - Daily schedule
  - [ ] `ci-nightly.yml` - Nightly schedule
  - [ ] `ci-performance.yml` - Weekly schedule
  - [ ] `crawler-test.yml` - Weekly schedule

### Disable Unnecessary Workflows
- [ ] Identify workflows you don't need
- [ ] Disable in GitHub UI:
  - [ ] **Actions** → Select workflow → **⋯** → **Disable workflow**
- [ ] Or delete workflow file and commit

### Customize Quality Thresholds
- [ ] Edit `ci-quality.yml` to adjust:
  - [ ] Coverage threshold (default: 70%)
  - [ ] Complexity limits (default: B)
  - [ ] Tech debt thresholds (default: 100)

---

## ✅ Phase 12: Team Onboarding (If Applicable)

### Share Documentation
- [ ] Share `docs/CI_CD_QUICKSTART.md` with team
- [ ] Add CI/CD section to onboarding docs
- [ ] Document workflow expectations

### Set Team Permissions
- [ ] Go to **Settings** → **Collaborators**
- [ ] Ensure team members have appropriate access
- [ ] Configure protected branches for team workflow

### Establish Workflow Practices
- [ ] Document PR process with CI requirements
- [ ] Establish merge requirements
- [ ] Define who can trigger manual workflows
- [ ] Set up code review requirements

---

## 🎯 Success Criteria

Your CI/CD pipeline is fully operational when:

- ✅ All CI workflows pass on main branch
- ✅ PR checks run automatically and block merge on failure
- ✅ Code coverage reports appear on PRs
- ✅ Scheduled workflows run without intervention
- ✅ Artifacts are generated and accessible
- ✅ Documentation site is live (if enabled)
- ✅ Team understands workflow processes
- ✅ Monitoring and alerts are configured

---

## 📊 Health Check

Run this health check weekly:

- [ ] Review failed workflows in last 7 days
- [ ] Check coverage trend (should be stable or improving)
- [ ] Review security scan results
- [ ] Check for outdated dependencies
- [ ] Review technical debt score
- [ ] Verify scheduled workflows ran successfully
- [ ] Check benchmark trends for regressions
- [ ] Update documentation if needed

---

## 🆘 Troubleshooting

If you encounter issues:

1. **Check workflow logs:**
   - Go to **Actions** → Failed workflow → Failed job → Expand failed step

2. **Review documentation:**
   - `docs/CI_CD_QUICKSTART.md` - Setup issues
   - `docs/CI_CD_PIPELINES.md` - Workflow details
   - `docs/CI_CD_TROUBLESHOOTING.md` - Common problems

3. **Enable debug mode:**
   - Add secret `ACTIONS_STEP_DEBUG` = `true`
   - Re-run workflow for verbose logs

4. **Re-run failed workflows:**
   - Open failed workflow run
   - Click **Re-run jobs** → **Re-run failed jobs**

5. **Check GitHub Status:**
   - Visit [githubstatus.com](https://githubstatus.com)
   - Verify Actions service is operational

---

## 📝 Notes

### First Run Considerations
- Ollama model download takes ~30 minutes on first run
- Subsequent runs are much faster (~15 min)
- Workflows cache dependencies for speed

### Cost Considerations
- Public repos: Free unlimited Actions minutes
- Private repos: Included minutes vary by plan
- Scheduled workflows count toward quota
- Consider disabling expensive workflows if on free tier

### Maintenance Schedule
- **Daily:** Review failed scheduled workflows
- **Weekly:** Check health metrics and trends
- **Monthly:** Update dependencies and review alerts
- **Quarterly:** Review and optimize workflows

---

## ✅ Completion

Once all phases are complete:

- [ ] Mark this checklist as done
- [ ] Archive this file or save for reference
- [ ] Set up recurring calendar reminders for maintenance
- [ ] Document any custom changes made
- [ ] Share success with team!

---

**Date Started:** _______________
**Date Completed:** _______________
**Completed By:** _______________

🎉 **Congratulations! Your BIRS CI/CD pipeline is fully operational!** 🎉

---

*Checklist version: 1.0*
*Last updated: 2024-01-XX*
