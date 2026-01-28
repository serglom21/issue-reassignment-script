#!/usr/bin/env python3
"""
Sentry Issue Reassignment Script

This script reassigns Sentry issues to align with CODEOWNERS assignments.
It compares current assignments with CODEOWNERS and fixes mismatches.
Supports pagination and includes a dry-run mode.
"""

import argparse
import sys
import requests
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs


class SentryIssueReassigner:
    """Handles reassignment of Sentry issues based on CODEOWNERS."""
    
    def __init__(self, auth_token: str, org_name: str, project_id: str, base_url: str = "https://us.sentry.io"):
        """
        Initialize the Sentry Issue Reassigner.
        
        Args:
            auth_token: Sentry API authentication token
            org_name: Organization slug
            project_id: Project ID (numeric)
            base_url: Sentry base URL (default: https://us.sentry.io)
        """
        self.auth_token = auth_token
        self.org_name = org_name
        self.project_id = project_id
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        })
    
    def fetch_issues(self, query: str, stats_period: str = "90d") -> List[Dict]:
        """
        Fetch all issues matching the query with owner information, handling pagination.
        
        Args:
            query: Sentry search query string
            stats_period: Stats period for the query (default: 14d)
            
        Returns:
            List of issue dictionaries with owner information
        """
        all_issues = []
        url = f"{self.base_url}/api/0/organizations/{self.org_name}/issues/"
        
        params = {
            'query': query,
            'project': self.project_id,
            'expand': 'owners',
            'collapse': 'stats',
            'shortIdLookup': '1',
            'statsPeriod': stats_period,
            'limit': 100  # Maximum items per page
        }
        
        page = 1
        while url:
            print(f"Fetching page {page}...", file=sys.stderr)
            
            try:
                response = self.session.get(url, params=params if page == 1 else None)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching issues: {e}", file=sys.stderr)
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Response status: {e.response.status_code}", file=sys.stderr)
                    print(f"Response content: {e.response.text}", file=sys.stderr)
                sys.exit(1)
            
            issues = response.json()
            all_issues.extend(issues)
            
            print(f"  Retrieved {len(issues)} issues (total so far: {len(all_issues)})", file=sys.stderr)
            
            # Check for next page in Link header
            url = self._get_next_page_url(response.headers.get('Link', ''))
            page += 1
            
            # Clear params for subsequent requests (URL already contains them)
            params = None
        
        return all_issues
    
    def _get_next_page_url(self, link_header: str) -> Optional[str]:
        """
        Parse the Link header to get the next page URL.
        
        Args:
            link_header: The Link header from the response
            
        Returns:
            Next page URL or None if no next page
        """
        if not link_header:
            return None
        
        links = link_header.split(',')
        for link in links:
            parts = link.strip().split(';')
            if len(parts) == 2:
                url = parts[0].strip()[1:-1]  # Remove < and >
                rel = parts[1].strip()
                if 'rel="next"' in rel and 'results="true"' in rel:
                    return url
        
        return None
    
    def get_codeowners_assignment(self, issue: Dict) -> Optional[str]:
        """
        Extract the CODEOWNERS assignment from an issue.
        
        Args:
            issue: Issue dictionary with owners information
            
        Returns:
            Assignee string in format 'team:<id>' or 'user:<id>', or None if no codeowners
        """
        owners = issue.get('owners', [])
        if not owners:
            return None
        
        # Find the first codeowners entry
        for owner in owners:
            if owner.get('type') == 'codeowners':
                owner_value = owner.get('owner')
                if owner_value:
                    # owner_value is in format 'team:12345' or 'user:12345'
                    return owner_value
        
        return None
    
    def needs_reassignment(self, issue: Dict) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if an issue needs reassignment based on CODEOWNERS.
        
        Args:
            issue: Issue dictionary
            
        Returns:
            Tuple of (needs_reassignment, current_assignment, codeowners_assignment)
        """
        assigned_to = issue.get('assignedTo')
        
        # Only process issues that are currently assigned to a team
        if not assigned_to or assigned_to.get('type') != 'team':
            return False, None, None
        
        current_team_id = str(assigned_to.get('id'))
        current_assignment = f"team:{current_team_id}"
        
        # Get the CODEOWNERS assignment
        codeowners_assignment = self.get_codeowners_assignment(issue)
        
        if not codeowners_assignment:
            # No codeowners defined for this issue
            return False, current_assignment, None
        
        # Extract team/user ID from codeowners assignment
        codeowners_type, codeowners_id = codeowners_assignment.split(':', 1)
        
        # Only reassign if it's a team assignment and IDs don't match
        if codeowners_type == 'team' and codeowners_id != current_team_id:
            return True, current_assignment, codeowners_assignment
        
        return False, current_assignment, codeowners_assignment
    
    def reassign_issue(self, issue_id: str, assignee: str) -> bool:
        """
        Reassign a single issue to the specified team or user.
        
        Args:
            issue_id: The issue ID
            assignee: The assignee in format 'team:<team_id>' or 'user:<user_id>'
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/api/0/issues/{issue_id}/"
        
        payload = {
            'assignedTo': assignee
        }
        
        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"  Error reassigning issue {issue_id}: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Response content: {e.response.text}", file=sys.stderr)
            return False
    
    def reassign_issues(self, query: str, stats_period: str = "90d", dry_run: bool = True) -> tuple:
        """
        Reassign all issues that don't match their CODEOWNERS assignment.
        
        Args:
            query: Sentry search query string
            stats_period: Stats period for the query
            dry_run: If True, only show what would be done without making changes
            
        Returns:
            Tuple of (total_checked, misaligned_issues, successful_reassignments)
        """
        print(f"\n{'='*80}")
        print(f"Sentry CODEOWNERS Issue Reassignment")
        print(f"{'='*80}")
        print(f"Organization: {self.org_name}")
        print(f"Project ID: {self.project_id}")
        print(f"Query: {query}")
        print(f"Stats Period: {stats_period}")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        print(f"{'='*80}\n")
        
        # Fetch all matching issues with owner information
        print("Fetching issues with owner information...\n")
        issues = self.fetch_issues(query, stats_period)
        
        total_checked = len(issues)
        print(f"\n{'='*80}")
        print(f"Found {total_checked} issue(s) matching the query")
        print(f"{'='*80}\n")
        
        if total_checked == 0:
            return 0, 0, 0
        
        # Analyze issues for misalignment
        print("Analyzing assignment alignment with CODEOWNERS...\n")
        misaligned_issues = []
        
        for issue in issues:
            needs_change, current, codeowners = self.needs_reassignment(issue)
            if needs_change:
                misaligned_issues.append({
                    'issue': issue,
                    'current_assignment': current,
                    'codeowners_assignment': codeowners
                })
        
        print(f"{'='*80}")
        print(f"Analysis Summary:")
        print(f"  Total issues checked: {total_checked}")
        print(f"  Misaligned issues (need reassignment): {len(misaligned_issues)}")
        print(f"  Correctly aligned issues: {total_checked - len(misaligned_issues)}")
        print(f"{'='*80}\n")
        
        if len(misaligned_issues) == 0:
            print("✓ All issues are correctly aligned with CODEOWNERS!")
            return total_checked, 0, 0
        
        # Display sample of misaligned issues
        print(f"Sample of misaligned issues (showing up to 10):\n")
        for i, item in enumerate(misaligned_issues[:10], 1):
            issue = item['issue']
            print(f"  {i}. Issue: {issue.get('id')} - {issue.get('title', 'No title')[:50]}")
            print(f"     Short ID: {issue.get('shortId', 'N/A')}")
            print(f"     Current assignment: {item['current_assignment']}")
            print(f"     CODEOWNERS assignment: {item['codeowners_assignment']}")
            print(f"     Status: {issue.get('status', 'unknown')}, "
                  f"Events: {issue.get('count', 0)}")
            print()
        
        if len(misaligned_issues) > 10:
            print(f"  ... and {len(misaligned_issues) - 10} more misaligned issue(s)\n")
        
        if dry_run:
            print("="*80)
            print("DRY RUN MODE: No changes will be made.")
            print(f"Would reassign {len(misaligned_issues)} issue(s) to match CODEOWNERS")
            print("="*80)
            return total_checked, len(misaligned_issues), 0
        
        # Perform actual reassignment
        print("="*80)
        print("Starting reassignment to align with CODEOWNERS...\n")
        successful = 0
        failed = 0
        
        for i, item in enumerate(misaligned_issues, 1):
            issue = item['issue']
            issue_id = issue.get('id')
            issue_short_id = issue.get('shortId', issue_id)
            issue_title = issue.get('title', 'No title')[:40]
            new_assignee = item['codeowners_assignment']
            
            print(f"  [{i}/{len(misaligned_issues)}] {issue_short_id}: {issue_title}")
            print(f"      {item['current_assignment']} → {new_assignee} ...", end=' ')
            
            if self.reassign_issue(issue_id, new_assignee):
                print("✓")
                successful += 1
            else:
                print("✗")
                failed += 1
        
        print(f"\n{'='*80}")
        print(f"Reassignment complete!")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total misaligned: {len(misaligned_issues)}")
        print(f"{'='*80}\n")
        
        return total_checked, len(misaligned_issues), successful


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Reassign Sentry issues to align with CODEOWNERS assignments.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script automatically detects and fixes assignment misalignments between
current team assignments and CODEOWNERS definitions.

It specifically handles case #2 from the assignment categories:
"Issues that report a new event post changes to CODEOWNERS and were manually 
assigned to the wrong team in the past"

The script will:
1. Fetch all issues matching your query with owner information
2. Compare current team assignments with CODEOWNERS assignments
3. Identify misaligned issues (where assignedTo team != CODEOWNERS team)
4. Reassign misaligned issues to match CODEOWNERS

Examples:
  # Dry run (default) - see what would be reassigned
  python reassign_sentry_issues.py \\
    --token YOUR_AUTH_TOKEN \\
    --org my-org \\
    --project-id 123456 \\
    --query "is:unresolved" \\
    --stats-period "30d"
  
  # Actually perform reassignment
  python reassign_sentry_issues.py \\
    --token YOUR_AUTH_TOKEN \\
    --org my-org \\
    --project-id 123456 \\
    --query "is:unresolved" \\
    --stats-period "30d" \\
    --no-dry-run
  
  # Check specific issues with events in last 7 days
  python reassign_sentry_issues.py \\
    --token YOUR_AUTH_TOKEN \\
    --org my-org \\
    --project-id 123456 \\
    --query "is:unresolved assigned:@team" \\
    --stats-period "7d" \\
    --no-dry-run

Query Examples:
  - "is:unresolved" - All unresolved issues
  - "is:unresolved assigned:@team" - Unresolved issues assigned to any team
  - "is:unresolved lastSeen:>2024-01-01" - Issues with recent events
  - "is:unresolved age:+30d" - Unresolved issues older than 30 days
        """
    )
    
    parser.add_argument(
        '--token',
        required=True,
        help='Sentry API authentication token'
    )
    parser.add_argument(
        '--org',
        required=True,
        help='Organization slug'
    )
    parser.add_argument(
        '--project-id',
        required=True,
        help='Project ID (numeric)'
    )
    parser.add_argument(
        '--query',
        default='is:unresolved',
        help='Sentry search query (default: "is:unresolved")'
    )
    parser.add_argument(
        '--stats-period',
        default='90d',
        help='Stats period for the query (default: 90d). Examples: 7d, 14d, 30d, 90d'
    )
    parser.add_argument(
        '--base-url',
        default='https://us.sentry.io',
        help='Sentry base URL (default: https://us.sentry.io)'
    )
    parser.add_argument(
        '--no-dry-run',
        action='store_true',
        help='Actually perform the reassignment (default is dry-run mode)'
    )
    
    args = parser.parse_args()
    
    # Create reassigner instance
    reassigner = SentryIssueReassigner(
        auth_token=args.token,
        org_name=args.org,
        project_id=args.project_id,
        base_url=args.base_url
    )
    
    # Perform reassignment analysis and execution
    dry_run = not args.no_dry_run
    total_checked, misaligned, successful = reassigner.reassign_issues(
        query=args.query,
        stats_period=args.stats_period,
        dry_run=dry_run
    )
    
    # Exit with appropriate status code
    if not dry_run and misaligned > 0 and successful < misaligned:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
