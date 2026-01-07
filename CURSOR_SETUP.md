# Cursor Setup Guide

## ✅ Virtual Environment Ready!

All Cursor settings have been configured automatically.

## 🚀 Quick Start

### 1. Reload Cursor

To make Cursor pick up the settings:
- **macOS:** `Cmd + Shift + P` → "Developer: Reload Window"
- Or simply close and reopen the project

### 2. Select Python Interpreter

After reloading, Cursor will automatically detect the `.venv` virtual environment.

**If this doesn't happen:**

1. Press `Cmd + Shift + P` (macOS)
2. Type: `Python: Select Interpreter`
3. Select: `Python 3.13.11 ('.venv': venv)`

**Or via status bar:**
- Click on Python version in the bottom right corner
- Select `.venv/bin/python`

### 3. Verify Installation

Open Cursor's integrated terminal (`Ctrl + ~` or `Cmd + ~`):

```bash
# Should show activated environment
which python
# Expected: /Users/voptunov/PycharmProjects/mobile_test_recorder/.venv/bin/python

python --version
# Expected: Python 3.13.11

observe --help
# Should display CLI help
```

## 📁 Created Configuration Files

### `.vscode/settings.json`
Main settings:
- ✅ Automatic virtual environment selection
- ✅ Automatic terminal activation
- ✅ Pytest configuration for testing
- ✅ Black formatting on save
- ✅ Flake8 and Mypy for code checking
- ✅ Auto-import and import organization

### `.vscode/extensions.json`
Recommended extensions:
- `ms-python.python` - Core Python extension
- `ms-python.vscode-pylance` - Enhanced IntelliSense
- `ms-python.black-formatter` - Code formatting
- `ms-python.flake8` - Linting
- `ms-python.mypy-type-checker` - Type checking

Cursor will suggest installing these extensions automatically.

### `.vscode/launch.json`
Debug configurations:
- **Python: Current File** - Debug current file
- **Python: Observe CLI** - Debug CLI commands
- **Python: Pytest - Current File** - Debug current test
- **Python: Pytest - All Tests** - Debug all tests
- **Python: Dashboard** - Debug web dashboard

## 🎯 Main Features

### 1. Automatic Formatting

When saving a file (Cmd + S), automatically:
- ✅ Format with Black
- ✅ Organize imports
- ✅ Remove unused imports

**To disable:** Remove `"editor.formatOnSave": true` in settings.json

### 2. Running Tests

#### Via UI:
1. Open the **Testing** tab (flask icon on the left)
2. Cursor will automatically find all pytest tests
3. Run tests by clicking ▶️

#### Via terminal:
```bash
pytest                    # All tests
pytest tests/test_file.py # Specific file
pytest -v                 # Verbose output
pytest -k "test_name"     # By name
```

### 3. Debugging

#### Method 1: Via breakpoints
1. Set a breakpoint (click left of line number)
2. `F5` or `Run → Start Debugging`
3. Select configuration (e.g., "Python: Current File")

#### Method 2: Via command
1. `Cmd + Shift + P`
2. Type: `Debug: Select and Start Debugging`
3. Select desired configuration

### 4. Linting and Type Checking

**Flake8** (automatic):
- Underlines code issues
- Shows warnings

**Mypy** (manual run):
```bash
mypy framework/
```

**Black** (formatting):
```bash
black .                    # Entire project
black framework/cli/       # Specific directory
```

### 5. IntelliSense and Auto-completion

Pylance provides:
- ✅ Code auto-completion
- ✅ Type hints
- ✅ Go to definition (Cmd + Click)
- ✅ Documentation on hover
- ✅ Refactoring (rename, extract method)

## 🔧 Integrated Terminal

Cursor automatically activates `.venv` when opening a new terminal.

**If environment doesn't activate:**
```bash
source .venv/bin/activate
```

**Or use full paths:**
```bash
.venv/bin/python
.venv/bin/pytest
.venv/bin/observe
```

## 📋 Useful Cursor Commands

| Command | Action |
|---------|--------|
| `Cmd + Shift + P` | Command Palette |
| `Cmd + P` | Quick file search |
| `Cmd + Shift + F` | Search in project |
| `Cmd + ~` | Open terminal |
| `F5` | Start debugging |
| `Shift + F5` | Stop debugging |
| `F9` | Set breakpoint |
| `F10` | Step Over (debugging) |
| `F11` | Step Into (debugging) |
| `Cmd + /` | Comment line |
| `Cmd + Shift + [` | Fold code block |
| `Cmd + Shift + ]` | Unfold code block |

## 🎨 Additional Settings (Optional)

### Customize Black Formatting

In `.vscode/settings.json` add:
```json
{
    "black-formatter.args": ["--line-length", "100"]
}
```

### Exclude Files from Search

Add to `.vscode/settings.json`:
```json
{
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.venv": true
    }
}
```

### Auto-save

```json
{
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1000
}
```

## 🐛 Troubleshooting

### Issue: Cursor doesn't see modules

**Solution:**
1. Check selected interpreter (should be `.venv/bin/python`)
2. Reload window: `Cmd + Shift + P` → "Developer: Reload Window"
3. Check `settings.json` → `python.analysis.extraPaths`

### Issue: "venv .venv subdirectory not found"

**Solution:**
1. Close Cursor completely
2. Verify `.venv` exists:
```bash
ls -la .venv/bin/python
```
3. Reopen Cursor
4. Select interpreter manually: `Cmd + Shift + P` → `Python: Select Interpreter`

### Issue: Tests not discovered

**Solution:**
1. Open Output panel: `View → Output`
2. Select "Python" from dropdown
3. Check for errors
4. Verify pytest is installed: `.venv/bin/pytest --version`

### Issue: Formatting doesn't work

**Solution:**
1. Install extension: `ms-python.black-formatter`
2. Check settings:
```json
{
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter"
    }
}
```

### Issue: Terminal doesn't activate environment

**Solution:**
1. Close all terminals
2. Open new terminal (`Cmd + ~`)
3. Or activate manually: `source .venv/bin/activate`

## 📚 Useful Links

- [Cursor Documentation](https://cursor.sh/docs)
- [Python in VSCode](https://code.visualstudio.com/docs/python/python-tutorial)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Code Style](https://black.readthedocs.io/)

## 🚀 Ready to Work!

Now you can:

1. ✅ **Write code** with auto-completion and type checking
2. ✅ **Run tests** via UI or terminal
3. ✅ **Debug** with breakpoints
4. ✅ **Format** automatically on save
5. ✅ **Use CLI** `observe` commands

### First Steps:

```bash
# In Cursor terminal
observe info              # Framework information
observe init              # Initialize project
pytest -v                 # Run tests
```

Happy coding! 🎉

---

**Created:** January 7, 2026  
**Python:** 3.13.11 (.venv)  
**Cursor:** Fully configured ✅
