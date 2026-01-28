#!/bin/bash

# Run script for Sentry Issue Reassignment Script
# This script activates the virtual environment and runs the main script

set -e  # Exit on any error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/venv"
MAIN_SCRIPT="$SCRIPT_DIR/reassign_sentry_issues.py"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Error: Virtual environment not found"
    echo ""
    echo "Please run setup first:"
    echo "  ./setup.sh"
    echo ""
    exit 1
fi

# Check if main script exists
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "❌ Error: Main script not found: $MAIN_SCRIPT"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Run the main script with all arguments passed to this script
python "$MAIN_SCRIPT" "$@"

# Capture exit code
EXIT_CODE=$?

# Deactivate virtual environment
deactivate

# Exit with the same code as the main script
exit $EXIT_CODE
