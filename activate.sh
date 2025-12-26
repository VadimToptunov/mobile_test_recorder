#!/bin/bash

# Activation script for Mobile Test Recorder virtual environment

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"

if [ ! -d "$VENV_PATH" ]; then
    echo " Virtual environment not found!"
    echo "Run: python3 -m venv .venv && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

echo " Virtual environment activated!"
echo ""
echo " Available commands:"
echo "  observe --help              # Show CLI help"
echo "  observe info                # Show framework info"
echo "  observe init                # Initialize new project"
echo ""
echo "🧪 Run tests:"
echo "  pytest                      # Run all tests"
echo "  pytest -v                   # Verbose mode"
echo ""
echo " Code quality:"
echo "  black .                     # Format code"
echo "  flake8 .                    # Lint code"
echo "  mypy framework              # Type check"
echo ""
echo " To deactivate: type 'deactivate'"
echo ""

