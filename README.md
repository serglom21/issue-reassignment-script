# Sentry Issue Reassignment Script

A Python script to bulk reassign Sentry issues matching a query to a specific team or user. The script handles pagination automatically and includes a dry-run mode for safe testing.

## Features

- 🔍 **Query-based filtering** - Use Sentry's search syntax to find specific issues
- 📄 **Automatic pagination** - Handles large result sets automatically
- 🧪 **Dry-run mode** - Preview what will be reassigned before making changes
- 👥 **Team and user assignment** - Support for both team and individual user assignment
- 📊 **Progress tracking** - Real-time progress updates and summary statistics
- ⚠️ **Error handling** - Graceful error handling with detailed error messages

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Syntax

```bash
python reassign_sentry_issues.py \
  --token YOUR_AUTH_TOKEN \
  --org your-org-slug \
  --project your-project-slug \
  --query "is:unresolved age:+30d" \
  --assignee "team:123456"
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--token` | Yes | Sentry API authentication token |
| `--org` | Yes | Organization slug |
| `--project` | Yes | Project slug |
| `--query` | Yes | Sentry search query string |
| `--assignee` | Yes | New assignee in format `team:<team_id>` or `user:<user_id>` |
| `--base-url` | No | Sentry base URL (default: `https://sentry.io`) |
| `--no-dry-run` | No | Actually perform reassignment (default is dry-run) |

### Getting Your Auth Token

1. Go to your Sentry account settings
2. Navigate to **Auth Tokens** or **API**
3. Create a new token with the following permissions:
   - `project:read`
   - `project:write`
   - `org:read`

### Finding Team and User IDs

#### Using Sentry Web Interface:
1. **For Teams**: Navigate to Settings → Teams → Select a team → Check the URL or use the browser console to inspect the team object
2. **For Users**: Navigate to Settings → Members → Select a user → Check the URL or use the browser console

#### Using Sentry API:
```bash
# List teams
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://sentry.io/api/0/organizations/YOUR_ORG/teams/

# List members
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://sentry.io/api/0/organizations/YOUR_ORG/members/
```

### Query Examples

| Query | Description |
|-------|-------------|
| `is:unresolved` | All unresolved issues |
| `is:unresolved age:+30d` | Unresolved issues older than 30 days |
| `is:unresolved age:+7d assigned:me` | Your unresolved issues older than 7 days |
| `is:ignored age:+90d` | Ignored issues older than 90 days |
| `is:unresolved level:error` | Unresolved error-level issues |
| `is:unresolved firstSeen:>2024-01-01` | Unresolved issues first seen after Jan 1, 2024 |

For more query syntax, see [Sentry's search documentation](https://docs.sentry.io/product/sentry-basics/search/).

## Examples

### 1. Dry Run (Preview Only)

Preview which issues would be reassigned without making any changes:

```bash
python reassign_sentry_issues.py \
  --token YOUR_AUTH_TOKEN \
  --org my-org \
  --project my-project \
  --query "is:unresolved age:+30d" \
  --assignee "team:123456"
```

**Output:**
```
======================================================================
Sentry Issue Reassignment
======================================================================
Organization: my-org
Project: my-project
Query: is:unresolved age:+30d
Assignee: team:123456
Mode: DRY RUN
======================================================================

Fetching issues...

Fetching page 1...
  Retrieved 100 issues (total so far: 100)
Fetching page 2...
  Retrieved 45 issues (total so far: 145)

======================================================================
Found 145 issue(s) matching the query
======================================================================

Sample of issues to be reassigned:
  1. MYPROJECT-ABC - TypeError: Cannot read property 'foo' of undefined
     Status: unresolved, Count: 234, Users: 56
  2. MYPROJECT-XYZ - ReferenceError: bar is not defined
     Status: unresolved, Count: 89, Users: 12
  ... and 143 more issue(s)

DRY RUN MODE: No changes will be made.
Would reassign 145 issue(s) to team:123456
```

### 2. Actual Reassignment

Perform the actual reassignment:

```bash
python reassign_sentry_issues.py \
  --token YOUR_AUTH_TOKEN \
  --org my-org \
  --project my-project \
  --query "is:unresolved age:+30d" \
  --assignee "team:123456" \
  --no-dry-run
```

### 3. Assign to a Specific User

```bash
python reassign_sentry_issues.py \
  --token YOUR_AUTH_TOKEN \
  --org my-org \
  --project my-project \
  --query "is:unresolved assigned:[me] age:+60d" \
  --assignee "user:789012" \
  --no-dry-run
```

### 4. Using Self-Hosted Sentry

```bash
python reassign_sentry_issues.py \
  --token YOUR_AUTH_TOKEN \
  --org my-org \
  --project my-project \
  --query "is:unresolved" \
  --assignee "team:123456" \
  --base-url "https://sentry.mycompany.com" \
  --no-dry-run
```

## Workflow Recommendations

1. **Always start with a dry run** to verify the query matches the expected issues
2. **Test with a limited query** first (e.g., add `age:+365d` to limit to very old issues)
3. **Review the sample output** to ensure you're targeting the right issues
4. **Run with `--no-dry-run`** only after confirming the dry run output

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
