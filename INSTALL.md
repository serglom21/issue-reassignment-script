# Installation Guide

This guide will help you set up the Sentry Issue Reassignment Script on any machine.

## Prerequisites

- **Python 3.7 or higher** must be installed on your system
- **Git** (if cloning from repository)
- **Bash shell** (Linux, macOS, or Git Bash on Windows)

## Quick Start

### 1. Clone or Download the Repository

```bash
# Clone from GitHub
git clone https://github.com/serglom21/issue-reassignment-script.git
cd issue-reassignment-script

# Or download and extract the ZIP file from GitHub
```

### 2. Run Setup

The setup script will create a virtual environment and install all dependencies:

```bash
./setup.sh
```

**What the setup script does:**
- Checks for Python 3.7+ installation
- Creates a Python virtual environment in `venv/`
- Upgrades pip to the latest version
- Installs all required dependencies from `requirements.txt`

### 3. Run the Script

Use the `run.sh` wrapper script to execute the main script:

```bash
# Dry run (preview only)
./run.sh \
  --token YOUR_AUTH_TOKEN \
  --org your-org-slug \
  --project-id 123456 \
  --query "is:unresolved assigned:@team" \
  --stats-period "30d"

# Actually perform reassignment
./run.sh \
  --token YOUR_AUTH_TOKEN \
  --org your-org-slug \
  --project-id 123456 \
  --query "is:unresolved assigned:@team" \
  --stats-period "30d" \
  --no-dry-run
```

## Manual Installation (Alternative)

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows (Git Bash):
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python reassign_sentry_issues.py --help
```

## Verifying Installation

To verify everything is set up correctly:

```bash
# Show help and available options
./run.sh --help
```

You should see the script's help message with all available options.

## Troubleshooting

### "python3: command not found"

**Problem:** Python 3 is not installed or not in your PATH.

**Solution:**
- **macOS:** Install Python 3 using Homebrew: `brew install python3`
- **Linux (Ubuntu/Debian):** `sudo apt-get install python3 python3-venv`
- **Windows:** Download from [python.org](https://www.python.org/downloads/)

### "Permission denied" when running scripts

**Problem:** Scripts don't have execute permissions.

**Solution:**
```bash
chmod +x setup.sh run.sh example_usage.sh reassign_sentry_issues.py
```

### Virtual environment issues

**Problem:** Virtual environment is corrupted or dependencies are outdated.

**Solution:**
```bash
# Remove and recreate virtual environment
rm -rf venv
./setup.sh
```

### Import errors

**Problem:** Dependencies not installed correctly.

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## Platform-Specific Notes

### macOS
- Works out of the box on most modern macOS versions
- Python 3 is pre-installed on macOS 12.3+

### Linux
- May need to install `python3-venv` package
- Ubuntu/Debian: `sudo apt-get install python3-venv`
- Fedora/RHEL: `sudo dnf install python3-virtualenv`

### Windows
- Use **Git Bash** or **WSL** (Windows Subsystem for Linux)
- Or modify scripts to use `.bat` files for native Windows support

## Using in CI/CD

The setup and run scripts are designed to work in CI/CD environments:

```bash
# CI/CD pipeline example
./setup.sh
./run.sh --token "$SENTRY_TOKEN" --org "$ORG" --project-id "$PROJECT_ID" --query "is:unresolved" --no-dry-run
```

## Environment Variables (Optional)

You can use environment variables instead of command-line arguments:

```bash
export SENTRY_AUTH_TOKEN="your-token-here"
export SENTRY_ORG="your-org"
export SENTRY_PROJECT_ID="123456"

./run.sh --token "$SENTRY_AUTH_TOKEN" --org "$SENTRY_ORG" --project-id "$SENTRY_PROJECT_ID" --query "is:unresolved"
```

## Uninstallation

To remove the virtual environment:

```bash
rm -rf venv/
```

To remove everything:

```bash
cd ..
rm -rf issue-reassignment-script/
```

## Getting Help

- See the main [README.md](README.md) for usage examples
- Run `./run.sh --help` for all available options
- Check [GitHub Issues](https://github.com/serglom21/issue-reassignment-script/issues) for known problems

## Next Steps

Once installed, see the [README.md](README.md) for:
- Detailed usage examples
- Query syntax
- Finding your Project ID
- Understanding the output
