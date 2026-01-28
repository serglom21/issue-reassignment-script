# Sentry Issue Reassignment Script

A Python script to automatically align Sentry issue assignments with CODEOWNERS definitions. The script detects misalignments between current team assignments and CODEOWNERS, then fixes them automatically. Handles pagination and includes a dry-run mode for safe testing.

## Problem Solved

This script addresses **Case #2**: Issues that report new events post-CODEOWNERS changes but were manually assigned to the wrong team in the past. The script:
- Compares current team assignments with CODEOWNERS definitions
- Identifies misaligned issues (where `assignedTo` team ≠ CODEOWNERS team)
- Automatically reassigns to the correct team per CODEOWNERS

## Features

- 🔍 **CODEOWNERS Integration** - Automatically detects correct assignments from CODEOWNERS
- 🎯 **Smart Detection** - Only reassigns issues with misalignments
- 📄 **Automatic pagination** - Handles large result sets automatically
- 🧪 **Dry-run mode** - Preview what will be reassigned before making changes
- 📊 **Detailed Analysis** - Shows alignment statistics and misalignment details
- ⚠️ **Error handling** - Graceful error handling with detailed error messages

## Quick Start

### 1. Setup (First Time Only)

```bash
# Clone the repository
git clone https://github.com/serglom21/issue-reassignment-script.git
cd issue-reassignment-script

# Run setup to create virtual environment and install dependencies
./setup.sh
```

### 2. Run the Script

```bash
# Dry run to check for misalignments
./run.sh \
  --token YOUR_AUTH_TOKEN \
  --org your-org-slug \
  --project-id 123456 \
  --query "is:unresolved assigned:@team" \
  --stats-period "30d"

# Actually fix misalignments
./run.sh \
  --token YOUR_AUTH_TOKEN \
  --org your-org-slug \
  --project-id 123456 \
  --query "is:unresolved assigned:@team" \
  --stats-period "30d" \
  --no-dry-run
```

See [INSTALL.md](INSTALL.md) for detailed installation instructions and troubleshooting.

## Manual Installation

If you prefer manual setup:

1. Clone or download this repository
2. Create virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: source venv/Scripts/activate
pip install -r requirements.txt
```

## Usage

### Basic Syntax

```bash
python reassign_sentry_issues.py \
  --token YOUR_AUTH_TOKEN \
  --org your-org-slug \
  --project-id 123456 \
  --query "is:unresolved" \
  --stats-period "30d"
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--token` | Yes | Sentry API authentication token |
| `--org` | Yes | Organization slug |
| `--project-id` | Yes | Project ID (numeric, not slug) |
| `--query` | Yes | Sentry search query string |
| `--stats-period` | No | Stats period for the query (default: `14d`). Examples: `7d`, `14d`, `30d` |
| `--base-url` | No | Sentry base URL (default: `https://us.sentry.io`) |
| `--no-dry-run` | No | Actually perform reassignment (default is dry-run) |

### Getting Your Auth Token

1. Go to your Sentry account settings
2. Navigate to **Auth Tokens** or **API**
3. Create a new token with the following permissions:
   - `project:read`
   - `project:write`
   - `org:read`

### Finding Your Project ID

The script requires a numeric Project ID (not the project slug). Here's how to find it:

#### Using Sentry Web Interface:
1. Navigate to **Settings → Projects → [Your Project]**
2. The Project ID is shown in the project settings page
3. Or check the URL when viewing the project - it often contains the project ID

#### Using Sentry API:
```bash
# List all projects in your organization
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://us.sentry.io/api/0/organizations/YOUR_ORG/projects/
```

The response will include `"id": 123456` for each project.

### Query Examples

| Query | Description | Use Case |
|-------|-------------|----------|
| `is:unresolved` | All unresolved issues | Check all active issues for misalignments |
| `is:unresolved assigned:@team` | Unresolved issues assigned to any team | Focus on team-assigned issues only |
| `is:unresolved lastSeen:>2024-01-01` | Issues with recent events after Jan 1 | Target issues with recent activity |
| `is:unresolved age:+30d` | Unresolved issues older than 30 days | Focus on older, still-active issues |
| `is:unresolved level:error` | Unresolved error-level issues | Prioritize high-severity issues |

**Recommended Query**: `is:unresolved assigned:@team` - This focuses on issues currently assigned to teams, which is what the script processes.

For more query syntax, see [Sentry's search documentation](https://docs.sentry.io/product/sentry-basics/search/).

## Examples

### 1. Dry Run (Preview Only)

Preview which issues have misaligned assignments without making any changes:

```bash
python reassign_sentry_issues.py \
  --token YOUR_AUTH_TOKEN \
  --org my-org \
  --project-id 123456 \
  --query "is:unresolved" \
  --stats-period "30d"
```

**Output:**
```
================================================================================
Sentry CODEOWNERS Issue Reassignment
================================================================================
Organization: my-org
Project ID: 123456
Query: is:unresolved
Stats Period: 30d
Mode: DRY RUN
================================================================================

Fetching issues with owner information...

Fetching page 1...
  Retrieved 100 issues (total so far: 100)
Fetching page 2...
  Retrieved 45 issues (total so far: 145)

================================================================================
Found 145 issue(s) matching the query
================================================================================

Analyzing assignment alignment with CODEOWNERS...

================================================================================
Analysis Summary:
  Total issues checked: 145
  Misaligned issues (need reassignment): 23
  Correctly aligned issues: 122
================================================================================

Sample of misaligned issues (showing up to 10):

  1. Issue: MYPROJECT-ABC - TypeError: Cannot read property 'foo' of undefined
     Short ID: MYPROJECT-1
     Current assignment: team:111111
     CODEOWNERS assignment: team:222222
     Status: unresolved, Events: 234

  2. Issue: MYPROJECT-XYZ - ReferenceError: bar is not defined
     Short ID: MYPROJECT-2
     Current assignment: team:111111
     CODEOWNERS assignment: team:333333
     Status: unresolved, Events: 89

  ... and 21 more misaligned issue(s)

================================================================================
DRY RUN MODE: No changes will be made.
Would reassign 23 issue(s) to match CODEOWNERS
================================================================================
```

### 2. Actual Reassignment

Perform the actual reassignment to align with CODEOWNERS:

```bash
python reassign_sentry_issues.py \
  --token YOUR_AUTH_TOKEN \
  --org my-org \
  --project-id 123456 \
  --query "is:unresolved" \
  --stats-period "30d" \
  --no-dry-run
```

### 3. Check Only Team-Assigned Issues

```bash
python reassign_sentry_issues.py \
  --token YOUR_AUTH_TOKEN \
  --org my-org \
  --project-id 123456 \
  --query "is:unresolved assigned:@team" \
  --stats-period "7d" \
  --no-dry-run
```

### 4. Using Self-Hosted Sentry

```bash
python reassign_sentry_issues.py \
  --token YOUR_AUTH_TOKEN \
  --org my-org \
  --project-id 123456 \
  --query "is:unresolved" \
  --stats-period "14d" \
  --base-url "https://sentry.mycompany.com" \
  --no-dry-run
```

## How It Works

The script automatically:
1. Fetches issues matching your query with CODEOWNERS information (`expand=owners`)
2. For each issue assigned to a team, compares the current team assignment with the CODEOWNERS team
3. Identifies misalignments where `assignedTo.id` ≠ CODEOWNERS team ID
4. Reassigns misaligned issues to the correct team per CODEOWNERS

**Note**: The script only processes issues currently assigned to teams. It will not reassign:
- Unassigned issues
- Issues assigned to individual users
- Issues where current team matches CODEOWNERS team
- Issues without CODEOWNERS definitions

## Workflow Recommendations

1. **Always start with a dry run** to see which issues are misaligned
2. **Review the analysis summary** to understand the scope of misalignments
3. **Check the sample output** to verify the reassignments make sense
4. **Run with `--no-dry-run`** only after confirming the dry run output
5. **Use appropriate stats-period** to focus on issues with recent events

## Error Handling

The script includes comprehensive error handling:

- **Invalid credentials**: Clear error message if auth token is invalid
- **Network errors**: Retries and detailed error messages for API failures
- **Invalid assignee format**: Validates assignee format before making API calls
- **Partial failures**: Continues processing if some reassignments fail and reports statistics

## Exit Codes

- `0`: Success (or dry-run completed)
- `1`: Error occurred (authentication, network, or partial failure in live mode)

## Limitations

- Requires appropriate Sentry API permissions
- Rate limiting may apply for very large result sets
- Maximum 100 issues per page (handled automatically by pagination)

## Troubleshooting

### "401 Unauthorized" Error
- Verify your auth token is valid and not expired
- Ensure the token has the required permissions (`project:read`, `project:write`)

### "404 Not Found" Error
- Double-check the organization and project slugs
- Ensure you have access to the specified project

### No Issues Found
- Verify your query syntax using Sentry's web interface search first
- Check that the project actually has issues matching your query

## Contributing

Feel free to submit issues or pull requests to improve this script!

## License

MIT License - feel free to use and modify as needed.
