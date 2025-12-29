# Phase 6 - Self-Healing Tests & Maintenance

## Overview

Phase 6 focuses on **automatic test maintenance** - the framework detects broken selectors during test failures and fixes them automatically. Plus a simple dashboard to review and approve the changes.

---

## Components

### 1. Self-Healing Selector Engine

**Problem**: UI changes break tests because selectors become invalid.

**Solution**: Automatically detect and fix broken selectors during test failures.

**How it works**:
1. Test fails because element not found
2. Framework captures page state
3. Tries alternative selector strategies (ID → XPath → CSS → Text)
4. Uses ML model to identify correct element
5. Validates healed selector on next run
6. Updates Page Object with new selector
7. Creates git commit with explanation

**Features**:
- Automatic failure analysis
- Multiple selector strategies with fallbacks
- ML-based element identification (reuse Phase 4 model)
- Confidence scoring (0.0 - 1.0)
- Page Object auto-update
- Git integration with detailed commits

**CLI**:
```bash
# Analyze failed tests
observe heal analyze --test-results ./failed-tests.xml

# Apply specific fix
observe heal apply --file pages/login_page.py --selector login_button

# Auto-heal all with high confidence
observe heal auto --min-confidence 0.8 --dry-run
observe heal auto --min-confidence 0.8 --commit
```

**Example**:
```python
# Before (broken):
class LoginPage:
    login_button = ("id", "btn_login")  # ID changed in app
    
# After auto-healing:
class LoginPage:
    # Auto-healed: 2025-01-29 23:45:12
    # Original: ("id", "btn_login") - element not found
    # New: XPath strategy, confidence: 0.92
    login_button = ("xpath", "//button[contains(@text, 'Login')]")
```

**Technical Details**:
- Hook into pytest failure reports
- Parse screenshot + page source at failure
- Extract all potential selectors for visible elements
- Score each selector using ML classifier
- Choose highest confidence match
- Update Python/Kotlin/Swift Page Object files
- Preserve git history with detailed messages

---

### 2. Test Maintenance Dashboard

**Problem**: Need visibility into test health and easy way to review auto-healed selectors.

**Solution**: Simple web dashboard showing test status and maintenance actions.

**Features**:

**Test Health View**:
- Pass/fail rate per test (last 30 runs)
- Flaky test detection (pass rate 20-80%)
- Average test duration
- Last failure timestamp
- Failure trends (chart)

**Healed Selectors Review**:
- List of auto-healed selectors pending approval
- Before/after selector comparison
- Confidence score
- Test run results after healing
- One-click approve/reject
- Bulk operations

**Test History**:
- Timeline of all test runs
- Filter by status, date, platform
- Drill down to specific failure
- View screenshots at failure
- Access logs

**Actions**:
- Approve healed selector → commits to git
- Reject → reverts to original
- Re-run specific test
- Disable flaky test temporarily
- Export maintenance report (PDF/CSV)

**Tech Stack**:
- Backend: FastAPI (simple REST API)
- Frontend: Plain HTML + Alpine.js (lightweight, no build step)
- Storage: SQLite (reuse existing Event Store schema)
- Auth: Simple token-based (optional)

**Access**:
```bash
observe dashboard start --port 8080
# Opens http://localhost:8080
```

**UI Pages**:
1. **Dashboard** - Overview, stats, charts
2. **Tests** - List of all tests with status
3. **Healed Selectors** - Review and approve fixes
4. **History** - Test execution timeline

---

## Implementation Plan

### Weeks 1-2: Healing Engine Core
- Failure detection hook
- Screenshot + page source capture
- Alternative selector extraction

### Weeks 3-4: ML Integration & Scoring
- Element identification using existing ML model
- Confidence scoring algorithm
- Selector validation

### Weeks 5-6: Auto-Update System
- Parse and update Page Object files (Python/Kotlin/Swift)
- Git integration (commit, diff, revert)
- CLI commands

### Weeks 7-8: Dashboard
- FastAPI backend with CRUD operations
- Simple HTML frontend
- Test history tracking
- Approval workflow

---

## Success Metrics

- **85%+** of broken selectors auto-healed successfully
- **70%** reduction in manual test maintenance time
- **< 2 minutes** to review and approve healed selector
- **50%** reduction in false positives (wrong element identified)

---

## Deliverables

### Code (~7,000 lines)
- Self-healing engine (~4,500 lines)
  - Failure analysis
  - Selector discovery
  - ML scoring
  - File updates
  - Git integration
  
- Maintenance dashboard (~2,500 lines)
  - FastAPI backend
  - HTML/Alpine.js frontend
  - SQLite schema extensions
  - Approval workflow

### Documentation
- Self-healing guide
- Dashboard user manual
- Configuration reference

---

## Timeline

**Duration**: 8 weeks

**Milestones**:
- Week 2: Basic healing works locally
- Week 4: ML integration complete
- Week 6: Auto-update with git commits
- Week 8: Dashboard ready for use

---

## Example Workflow

```bash
# 1. Run tests (some fail due to UI changes)
pytest tests/ --junit-xml=results.xml

# 2. Analyze failures
observe heal analyze --test-results results.xml
# Output: Found 5 selector failures, 4 can be auto-healed

# 3. Apply fixes (dry run first)
observe heal auto --min-confidence 0.8 --dry-run
# Shows what would be changed

# 4. Apply for real
observe heal auto --min-confidence 0.8 --commit
# Updates Page Objects, commits to git

# 5. Review in dashboard
observe dashboard start
# Open browser, review changes, approve/reject

# 6. Re-run tests
pytest tests/
# All pass!
```

---

**Phase 6: Simple, focused, valuable.** 🎯

**2 components. 8 weeks. ~7,000 lines.**
