#!/bin/bash

# Example Usage Script for Sentry CODEOWNERS Issue Reassignment
# 
# IMPORTANT: Replace the placeholder values below with your actual values
# before running this script.

# Configuration
SENTRY_TOKEN="your-auth-token-here"
ORG_SLUG="your-org-slug"
PROJECT_ID="123456"  # Replace with actual numeric project ID

# Example 1: Dry run - Check all unresolved issues for misalignments
echo "Example 1: Dry run - Check all unresolved issues"
echo "This will show which issues have misaligned assignments"
python reassign_sentry_issues.py \
  --token "$SENTRY_TOKEN" \
  --org "$ORG_SLUG" \
  --project-id "$PROJECT_ID" \
  --query "is:unresolved" \
  --stats-period "30d"

echo ""
echo "Press Enter to continue to the next example..."
read

# Example 2: Dry run - Check only team-assigned issues
echo "Example 2: Dry run - Check team-assigned issues only"
echo "This focuses on issues currently assigned to teams"
python reassign_sentry_issues.py \
  --token "$SENTRY_TOKEN" \
  --org "$ORG_SLUG" \
  --project-id "$PROJECT_ID" \
  --query "is:unresolved assigned:@team" \
  --stats-period "14d"

echo ""
echo "Press Enter to continue to the next example..."
read

# Example 3: Actually fix misalignments
echo "Example 3: Actually reassign misaligned issues"
echo "WARNING: This will modify issue assignments!"
python reassign_sentry_issues.py \
  --token "$SENTRY_TOKEN" \
  --org "$ORG_SLUG" \
  --project-id "$PROJECT_ID" \
  --query "is:unresolved assigned:@team" \
  --stats-period "30d" \
  --no-dry-run

echo ""
echo "All examples completed!"
