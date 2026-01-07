# Virtual Environment Setup

## ✅ Virtual Environment Created!

### Environment Information

- **Python Version:** 3.13.11
- **Location:** `.venv/`
- **Installed Packages:** 102

### Activating the Environment

#### Option 1: Using activation script (recommended)
```bash
source activate.sh
```

#### Option 2: Direct activation
```bash
source .venv/bin/activate
```

#### Option 3: In PyCharm
1. Open project settings: `File → Settings → Project → Python Interpreter`
2. Click the gear icon → `Add`
3. Select `Existing environment`
4. Specify path: `/Users/voptunov/PycharmProjects/mobile_test_recorder/.venv/bin/python`

#### Option 4: In Cursor
1. `Cmd + Shift + P` → `Python: Select Interpreter`
2. Select: `Python 3.13.11 ('.venv': venv)`
3. Or click on Python version in bottom right corner

### Main Commands

After activating the environment, the following commands are available:

#### Framework CLI
```bash
observe --help              # Show help
observe info                # Framework information
observe init                # Initialize new project
observe record              # Record session
observe generate            # Generate tests
```

#### Testing
```bash
pytest                      # Run all tests
pytest -v                   # Verbose output
pytest -k "test_name"       # Run specific test
pytest --cov=framework      # With code coverage
pytest -n auto              # Parallel execution (xdist)
```

#### Code Quality
```bash
black .                     # Format code
flake8 .                    # Style checking
mypy framework              # Type checking
```

#### Dashboard
```bash
observe dashboard start     # Start web dashboard
```

### Deactivation
```bash
deactivate
```

### Installed Main Packages

#### Testing
- `pytest` (9.0.2) - Main testing framework
- `pytest-bdd` (8.1.0) - BDD testing
- `pytest-xdist` (3.8.0) - Parallel execution
- `pytest-cov` (7.0.0) - Code coverage
- `allure-pytest` (2.15.3) - Allure reports

#### Mobile Testing
- `appium-python-client` (5.2.4) - Appium client
- `selenium` (4.39.0) - Selenium WebDriver

#### ML & Data Science
- `scikit-learn` (1.8.0) - Machine Learning
- `pandas` (2.3.3) - Data analysis
- `numpy` (2.2.6) - Scientific computing
- `joblib` (1.5.3) - Model persistence

#### Visualization & Analytics
- `matplotlib` (3.10.8) - Visualization
- `seaborn` (0.13.2) - Statistical visualization
- `plotly` (6.5.0) - Interactive graphs

#### Computer Vision
- `opencv-python` (4.12.0.88) - Image processing
- `pillow` (12.1.0) - Image manipulation
- `pytesseract` (0.3.13) - OCR (text recognition)

#### Backend
- `fastapi` (0.128.0) - Web framework
- `uvicorn` (0.40.0) - ASGI server
- `sqlalchemy` (2.0.45) - Database ORM

#### Development Tools
- `black` (25.12.0) - Code formatting
- `flake8` (7.3.0) - Linter
- `mypy` (1.19.1) - Type checking

#### Integrations
- `slack-sdk` (3.39.0) - Slack notifications
- `gitpython` (3.1.46) - Git integration
- `junitparser` (4.0.2) - JUnit XML parsing

### Reinstalling Dependencies

If you need to reinstall dependencies:

```bash
# Remove environment
rm -rf .venv

# Create anew
/opt/homebrew/bin/python3.13 -m venv .venv

# Install dependencies
.venv/bin/pip install --upgrade pip setuptools wheel
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
```

### Troubleshooting

#### Python 3.13 not found
```bash
# Install via Homebrew
brew install python@3.13
```

#### Package installation errors
```bash
# Update pip
.venv/bin/pip install --upgrade pip

# Install with verbose flag for diagnostics
.venv/bin/pip install -r requirements.txt -v
```

#### PyCharm doesn't see packages
1. Close the project
2. Delete `.idea` folder
3. Reopen the project
4. Specify interpreter: `.venv/bin/python`

#### Cursor shows "venv .venv subdirectory not found"
```bash
# Check that .venv exists
ls -la .venv/bin/python

# If it exists, reload Cursor
# Cmd + Shift + P → "Developer: Reload Window"

# Select interpreter manually
# Cmd + Shift + P → "Python: Select Interpreter"
```

### Updating Dependencies

#### Update all packages to latest versions
```bash
.venv/bin/pip list --outdated              # Check outdated packages
.venv/bin/pip install --upgrade <package>  # Update specific package
```

#### Update requirements.txt
```bash
# After updating packages
.venv/bin/pip freeze > requirements.txt
```

### Exporting and Importing Environment

#### Export package list
```bash
.venv/bin/pip freeze > requirements-exact.txt  # With exact versions
.venv/bin/pip list --format=json > packages.json  # In JSON format
```

#### Create environment on another machine
```bash
# On new machine
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### Useful Links

- [README.md](README.md) - Main documentation
- [USER_GUIDE.md](USER_GUIDE.md) - User guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Developer guide
- [CHANGELOG.md](CHANGELOG.md) - Change history
- [CURSOR_SETUP.md](CURSOR_SETUP.md) - Cursor setup

### Project Structure

```
mobile_test_recorder/
├── .venv/                 # Virtual environment (102 packages)
│   ├── bin/              # Executables (python, pip, observe, pytest)
│   ├── lib/              # Installed libraries
│   └── pyvenv.cfg        # Environment config
├── framework/            # Main framework code
│   ├── cli/             # CLI interface
│   ├── ml/              # Machine learning
│   ├── analyzers/       # Code analyzers
│   ├── healing/         # Self-healing tests
│   └── ...
├── demo-app/            # Demo applications (Android & iOS)
├── requirements.txt     # Project dependencies
├── pyproject.toml       # Project configuration
├── activate.sh          # Activation script
└── README.md            # Documentation
```

### Environment Health Check

```bash
# Check Python version
.venv/bin/python --version

# Check installed packages
.venv/bin/pip list

# Check dependency conflicts
.venv/bin/pip check

# Check CLI functionality
.venv/bin/observe --version

# Check pytest
.venv/bin/pytest --version

# Run quick test
.venv/bin/python -c "import framework; print('✅ Framework imported successfully')"
```

### Performance

The virtual environment is optimized for:
- ✅ Fast test execution (pytest-xdist)
- ✅ Parallel processing (joblib, multiprocessing)
- ✅ Efficient image handling (opencv, pillow)
- ✅ Fast machine learning (scikit-learn with numpy/scipy)

### Usage Tips

1. **Always activate environment** before working
2. **Use `observe` CLI** for main operations
3. **Run tests regularly** with `pytest`
4. **Format code** with `black` before committing
5. **Check types** with `mypy`

---

**Created:** January 7, 2026  
**Python Version:** 3.13.11  
**Status:** ✅ Ready to use

