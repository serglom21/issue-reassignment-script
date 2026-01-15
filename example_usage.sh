#!/bin/bash

# Example Usage Script for Sentry Issue Reassignment
# 
# IMPORTANT: Replace the placeholder values below with your actual values
# before running this script.

# Configuration
SENTRY_TOKEN="your-auth-token-here"
ORG_SLUG="your-org-slug"
PROJECT_SLUG="your-project-slug"
TEAM_ID="123456"  # Replace with actual team ID
USER_ID="789012"  # Replace with actual user ID

# Example 1: Dry run - Reassign old unresolved issues to a team
echo "Example 1: Dry run - Preview reassigning old issues"
python reassign_sentry_issues.py \
  --token "$SENTRY_TOKEN" \
  --org "$ORG_SLUG" \
  --project "$PROJECT_SLUG" \
  --query "is:unresolved age:+30d" \
  --assignee "team:$TEAM_ID"

echo ""
echo "Press Enter to continue to the next example..."
read

# Example 2: Actual reassignment of very old issues
echo "Example 2: Actually reassign very old issues (90+ days)"
python reassign_sentry_issues.py \
  --token "$SENTRY_TOKEN" \
  --org "$ORG_SLUG" \
  --project "$PROJECT_SLUG" \
  --query "is:unresolved age:+90d" \
  --assignee "team:$TEAM_ID" \
  --no-dry-run

echo ""
echo "Press Enter to continue to the next example..."
read

# Example 3: Reassign ignored issues to a specific user
echo "Example 3: Reassign old ignored issues to a user"
python reassign_sentry_issues.py \
  --token "$SENTRY_TOKEN" \
  --org "$ORG_SLUG" \
  --project "$PROJECT_SLUG" \
  --query "is:ignored age:+60d" \
  --assignee "user:$USER_ID" \
  --no-dry-run

echo ""
echo "All examples completed!"
