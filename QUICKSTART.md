# Quick Start Guide

Get started with the Sentry Issue Reassignment Script in 3 simple steps.

## 📦 Step 1: Setup (First Time Only)

```bash
git clone https://github.com/serglom21/issue-reassignment-script.git
cd issue-reassignment-script
./setup.sh
```

**What this does:**
- ✓ Creates a Python virtual environment
- ✓ Installs all dependencies
- ✓ Verifies Python 3.7+ is installed

Takes ~30 seconds. You only need to do this once!

---

## 🔍 Step 2: Dry Run (Preview Changes)

```bash
./run.sh \
  --token YOUR_SENTRY_AUTH_TOKEN \
  --org your-org-slug \
  --project-id 123456 \
  --query "is:unresolved assigned:@team" \
  --stats-period "30d"
```

**What this does:**
- Fetches all issues matching your query
- Compares current assignments with CODEOWNERS
- Shows which issues are misaligned
- **Does NOT make any changes** (safe to run)

---

## ✅ Step 3: Fix Misalignments

After reviewing the dry run output, fix the misalignments:

```bash
./run.sh \
  --token YOUR_SENTRY_AUTH_TOKEN \
  --org your-org-slug \
  --project-id 123456 \
  --query "is:unresolved assigned:@team" \
  --stats-period "30d" \
  --no-dry-run
```

**What this does:**
- Reassigns misaligned issues to match CODEOWNERS
- Shows progress for each issue
- Reports success/failure statistics

---

## 🔑 Required Information

Before running, you'll need:

1. **Sentry Auth Token**
   - Go to Sentry → Settings → Account → Auth Tokens
   - Create token with `project:read` and `project:write` scopes

2. **Organization Slug**
   - Found in your Sentry URL: `https://sentry.io/organizations/YOUR-ORG-SLUG/`

3. **Project ID** (numeric)
   - Go to Project Settings
   - Look for "Project ID" field (e.g., `123456`)

---

## 📊 Understanding the Output

### Dry Run Output:
```
Analysis Summary:
  Total issues checked: 145
  Misaligned issues (need reassignment): 23
  Correctly aligned issues: 122
```

- **Misaligned issues**: Current team doesn't match CODEOWNERS team
- **Correctly aligned**: Current team matches CODEOWNERS team

### Sample Misaligned Issue:
```
Issue: MYPROJECT-ABC - TypeError: Cannot read...
  Current assignment: team:111111
  CODEOWNERS assignment: team:222222
```

This issue is assigned to team `111111` but CODEOWNERS says it should be `222222`.

---

## ⚙️ Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--query` | Filter which issues to check | `"is:unresolved"` |
| `--stats-period` | Time window for issue events | `"7d"`, `"14d"`, `"30d"` |
| `--no-dry-run` | Actually make changes | (flag, no value) |

---

## 💡 Pro Tips

1. **Always start with a dry run** to preview changes
2. **Use specific queries** to target specific issues:
   - `"is:unresolved assigned:@team"` - Only team-assigned issues
   - `"is:unresolved lastSeen:>2024-01-01"` - Recent activity only
3. **Adjust stats-period** based on your needs:
   - `"7d"` - Focus on very recent issues
   - `"30d"` - Broader scope (recommended)
   - `"90d"` - Very old issues
4. **Check the sample output** before running with `--no-dry-run`

---

## 🆘 Need Help?

- **Full documentation**: See [README.md](README.md)
- **Installation issues**: See [INSTALL.md](INSTALL.md)
- **Script help**: Run `./run.sh --help`
- **Report issues**: [GitHub Issues](https://github.com/serglom21/issue-reassignment-script/issues)

---

## 🎯 What Problem Does This Solve?

After updating CODEOWNERS, some issues might still be assigned to the old (wrong) team. This script:
- ✓ Finds issues with misaligned assignments
- ✓ Automatically reassigns them to the correct team per CODEOWNERS
- ✓ Only touches issues that need fixing

**Case #2**: Issues that report new events post-CODEOWNERS changes but were manually assigned to the wrong team.

---

## 📝 Example Workflow

```bash
# 1. Setup (first time only)
./setup.sh

# 2. Preview what would change
./run.sh --token abc123 --org my-company --project-id 456789 \
  --query "is:unresolved assigned:@team" --stats-period "30d"

# 3. Review output, then fix misalignments
./run.sh --token abc123 --org my-company --project-id 456789 \
  --query "is:unresolved assigned:@team" --stats-period "30d" --no-dry-run

# Done! ✓
```
