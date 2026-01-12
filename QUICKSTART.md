# Mobile Test Recorder - Quick Start Guide

> Get up and running in 10 minutes ⏱️

---

## Installation

```bash
# Clone repository
git clone https://github.com/VadimToptunov/mobile_test_recorder.git
cd mobile_test_recorder

# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Verify installation
observe info
```

---

## Available Commands

The framework provides four main command groups:

### 1. Business Logic Analysis
```bash
# Analyze Android/iOS source code for business rules, edge cases, and patterns
observe business-logic analyze <source_path> --output analysis.json
observe business-logic report analysis.json     # Human-readable report
observe business-logic stats analysis.json      # Statistics summary
```

### 2. Project Integration
```bash
# Full automation: analyze + generate tests in one command
observe project fullcycle \
  --android-source path/to/android/src \
  --ios-source path/to/ios/src \
  --output ./tests/

# Individual steps:
observe project analyze <source_path> --output analysis.json
observe project integrate analysis.json --framework-path ./my-tests/
observe project generate analysis.json --output ./tests/
```

### 3. Session Recording
```bash
# (Coming soon - SDK integration required)
observe record start --session-id my-session
observe record stop
observe record correlate <session_id>
```

### 4. Test Generation
```bash
# (Coming soon - generates from recorded sessions)
observe generate pages --model app-model.json --output tests/pages/
observe generate api --model app-model.json --output tests/api/
```

---

## Basic Workflow

### Scenario 1: Analyze Existing App

**Goal:** Extract business logic from your mobile app source code

```bash
# 1. Navigate to your project
cd /path/to/your/mobile/app

# 2. Analyze source code
observe business-logic analyze ./src/main --output analysis.json

# 3. View results
observe business-logic report analysis.json

# 4. See statistics
observe business-logic stats analysis.json
```

**Output:**
- User flows discovered
- Business rules extracted
- Edge cases identified
- API contracts generated
- Negative test cases suggested

---

### Scenario 2: Generate Tests from Analysis

**Goal:** Auto-generate Page Objects and tests

```bash
# 1. Analyze Android app
observe project analyze ./android/src --platform android --output android-analysis.json

# 2. Generate complete test suite
observe project generate android-analysis.json \
  --output ./tests/ \
  --framework pytest-bdd

# 3. Run generated tests
pytest tests/ -v
```

**Generated:**
- `tests/pages/` - Page Objects
- `tests/api/` - API clients
- `tests/features/` - BDD scenarios (if applicable)

---

### Scenario 3: Full Automation (Android + iOS)

**Goal:** One command to analyze and generate everything

```bash
observe project fullcycle \
  --android-source ./android/app/src/main \
  --ios-source ./ios/MyApp \
  --output ./tests/ \
  --platform both
```

**What happens:**
1. ✅ Analyzes Android source code
2. ✅ Analyzes iOS source code
3. ✅ Extracts API contracts
4. ✅ Generates Page Objects
5. ✅ Creates integration tests
6. ✅ Produces BDD features

**Time:** ~2-5 minutes for typical app

---

## Understanding the Analysis

### Business Logic Analysis Output

```json
{
  "user_flows": [
    {
      "name": "User Login",
      "steps": ["Launch app", "Enter email", "Enter password", "Submit"],
      "priority": "high"
    }
  ],
  "edge_cases": [
    {
      "type": "boundary",
      "description": "Age check: age >= 18",
      "test_data": [17, 18, 19, 100],
      "severity": "high"
    }
  ],
  "api_contracts": [
    {
      "endpoint": "/api/v1/auth/login",
      "method": "POST",
      "request_schema": {"email": "string", "password": "string"},
      "expected_responses": [200, 401, 400]
    }
  ]
}
```

---

## Command Reference

### Business Logic Commands

| Command | Description | Example |
|---------|-------------|---------|
| `analyze` | Analyze source code | `observe business-logic analyze ./src --output result.json` |
| `report` | Generate human-readable report | `observe business-logic report result.json` |
| `stats` | Show statistics summary | `observe business-logic stats result.json` |

### Project Commands

| Command | Description | Example |
|---------|-------------|---------|
| `analyze` | Analyze project source | `observe project analyze ./src --platform android` |
| `integrate` | Integrate with existing tests | `observe project integrate analysis.json --framework-path ./tests` |
| `generate` | Generate test artifacts | `observe project generate analysis.json --output ./tests` |
| `fullcycle` | Do everything at once | `observe project fullcycle --android-source ./android/src --output ./tests` |

---

## Common Use Cases

### 1. Audit Existing App
```bash
# Quick analysis to understand app structure
observe business-logic analyze ./src --output audit.json
observe business-logic report audit.json > audit-report.txt

# Share report with team
cat audit-report.txt
```

### 2. Add Tests to Legacy App
```bash
# Generate tests from existing codebase
observe project fullcycle \
  --android-source ./app/src/main \
  --output ./tests/generated/

# Review generated tests
ls -la tests/generated/
```

### 3. API Contract Extraction
```bash
# Extract all API endpoints
observe business-logic analyze ./src --output api-analysis.json

# View API contracts
observe business-logic report api-analysis.json | grep -A 10 "API Contracts"
```

---

## Next Steps

1. **Read Full Documentation:** [USER_GUIDE.md](USER_GUIDE.md)
2. **Try Demo Apps:** `cd demo-app/` (Android & iOS examples included)
3. **View Examples:** Check `tests/` directory for sample outputs
4. **Report Issues:** [GitHub Issues](https://github.com/VadimToptunov/mobile_test_recorder/issues)

---

## Troubleshooting

### Issue: "No business logic detected"

**Cause:** Source path doesn't contain Kotlin/Swift/Java files

**Solution:**
```bash
# Check if files exist
find ./src -name "*.kt" -o -name "*.swift" -o -name "*.java"

# Use correct source path
observe business-logic analyze ./app/src/main  # Android
observe business-logic analyze ./MyApp/MyApp   # iOS
```

### Issue: "Command not found: observe"

**Cause:** Framework not installed in PATH

**Solution:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Reinstall in editable mode
pip install -e .

# Verify
observe info
```

### Issue: "Empty analysis result"

**Cause:** Unsupported file type or parsing error

**Solution:**
```bash
# Enable debug logging
export OBSERVE_LOG_LEVEL=DEBUG
observe business-logic analyze ./src --output result.json

# Check logs
cat ~/.observe/logs/observe.log
```

---

## Tips for Best Results

✅ **Do:**
- Use actual project source code (not compiled binaries)
- Point to source directories (e.g., `./app/src/main`)
- Review generated tests before committing
- Iterate: analyze → review → refine → re-generate

❌ **Don't:**
- Point to build directories (`./build`, `./out`)
- Analyze compiled files (`.apk`, `.ipa`)
- Skip reviewing auto-generated code
- Expect 100% perfect generation (it's AI-assisted, not magic!)

---

## Getting Help

### Quick Help
```bash
observe --help                    # All commands
observe business-logic --help     # Business logic commands
observe project --help            # Project commands
```

### Resources
- **Documentation:** [USER_GUIDE.md](USER_GUIDE.md) (complete reference)
- **Examples:** `demo-app/` directory
- **Issues:** [GitHub Issues](https://github.com/VadimToptunov/mobile_test_recorder/issues)

---

**Ready to automate your testing!** 🚀

For detailed scenarios and advanced features, see the [complete user guide](USER_GUIDE.md).
