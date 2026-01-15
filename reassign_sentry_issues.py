#!/usr/bin/env python3
"""
Sentry Issue Reassignment Script

This script reassigns Sentry issues matching a query to a specified team or user.
It supports pagination and includes a dry-run mode.
"""

import argparse
import sys
import requests
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, parse_qs


class SentryIssueReassigner:
    """Handles reassignment of Sentry issues."""
    
    def __init__(self, auth_token: str, org_name: str, project_name: str, base_url: str = "https://sentry.io"):
        """
        Initialize the Sentry Issue Reassigner.
        
        Args:
            auth_token: Sentry API authentication token
            org_name: Organization slug
            project_name: Project slug
            base_url: Sentry base URL (default: https://sentry.io)
        """
        self.auth_token = auth_token
        self.org_name = org_name
        self.project_name = project_name
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        })
    
    def fetch_issues(self, query: str) -> List[Dict]:
        """
        Fetch all issues matching the query, handling pagination.
        
        Args:
            query: Sentry search query string
            
        Returns:
            List of issue dictionaries
        """
        all_issues = []
        url = f"{self.base_url}/api/0/projects/{self.org_name}/{self.project_name}/issues/"
        
        params = {
            'query': query,
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
    
    def reassign_issues(self, query: str, assignee: str, dry_run: bool = True) -> tuple:
        """
        Reassign all issues matching the query.
        
        Args:
            query: Sentry search query string
            assignee: The assignee in format 'team:<team_id>' or 'user:<user_id>'
            dry_run: If True, only show what would be done without making changes
            
        Returns:
            Tuple of (total_issues, successful_reassignments)
        """
        print(f"\n{'='*70}")
        print(f"Sentry Issue Reassignment")
        print(f"{'='*70}")
        print(f"Organization: {self.org_name}")
        print(f"Project: {self.project_name}")
        print(f"Query: {query}")
        print(f"Assignee: {assignee}")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        print(f"{'='*70}\n")
        
        # Fetch all matching issues
        print("Fetching issues...\n")
        issues = self.fetch_issues(query)
        
        total_issues = len(issues)
        print(f"\n{'='*70}")
        print(f"Found {total_issues} issue(s) matching the query")
        print(f"{'='*70}\n")
        
        if total_issues == 0:
            return 0, 0
        
        # Display sample of issues
        print("Sample of issues to be reassigned:")
        for i, issue in enumerate(issues[:5], 1):
            print(f"  {i}. {issue.get('id')} - {issue.get('title', 'No title')[:60]}")
            print(f"     Status: {issue.get('status', 'unknown')}, "
                  f"Count: {issue.get('count', 0)}, "
                  f"Users: {issue.get('userCount', 0)}")
        
        if total_issues > 5:
            print(f"  ... and {total_issues - 5} more issue(s)")
        
        print()
        
        if dry_run:
            print("DRY RUN MODE: No changes will be made.")
            print(f"Would reassign {total_issues} issue(s) to {assignee}")
            return total_issues, 0
        
        # Perform actual reassignment
        print("Starting reassignment...\n")
        successful = 0
        failed = 0
        
        for i, issue in enumerate(issues, 1):
            issue_id = issue.get('id')
            issue_title = issue.get('title', 'No title')[:50]
            
            print(f"  [{i}/{total_issues}] Reassigning {issue_id} - {issue_title}...", end=' ')
            
            if self.reassign_issue(issue_id, assignee):
                print("✓")
                successful += 1
            else:
                print("✗")
                failed += 1
        
        print(f"\n{'='*70}")
        print(f"Reassignment complete!")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total: {total_issues}")
        print(f"{'='*70}\n")
        
        return total_issues, successful


def validate_assignee(assignee: str) -> bool:
    """
    Validate the assignee format.
    
    Args:
        assignee: The assignee string
        
    Returns:
        True if valid, False otherwise
    """
    if not assignee:
        return False
    
    if assignee.startswith('team:') or assignee.startswith('user:'):
        parts = assignee.split(':', 1)
        return len(parts) == 2 and parts[1].strip()
    
    return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Reassign Sentry issues matching a query to a team or user.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (default) - see what would be reassigned
  python reassign_sentry_issues.py \\
    --token YOUR_AUTH_TOKEN \\
    --org my-org \\
    --project my-project \\
    --query "is:unresolved age:+30d" \\
    --assignee "team:123456"
  
  # Actually perform reassignment
  python reassign_sentry_issues.py \\
    --token YOUR_AUTH_TOKEN \\
    --org my-org \\
    --project my-project \\
    --query "is:unresolved age:+30d" \\
    --assignee "team:123456" \\
    --no-dry-run
  
  # Assign to a specific user
  python reassign_sentry_issues.py \\
    --token YOUR_AUTH_TOKEN \\
    --org my-org \\
    --project my-project \\
    --query "is:unresolved" \\
    --assignee "user:789012" \\
    --no-dry-run

Assignee Format:
  - For teams: team:<team_id> (e.g., team:123456)
  - For users: user:<user_id> (e.g., user:789012)
  
  You can find team and user IDs in Sentry's web interface or API.

Query Examples:
  - "is:unresolved" - All unresolved issues
  - "is:unresolved age:+30d" - Unresolved issues older than 30 days
  - "is:unresolved age:+7d assigned:me" - Your unresolved issues older than 7 days
  - "is:ignored age:+90d" - Ignored issues older than 90 days
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
        '--project',
        required=True,
        help='Project slug'
    )
    parser.add_argument(
        '--query',
        required=True,
        help='Sentry search query (e.g., "is:unresolved age:+30d")'
    )
    parser.add_argument(
        '--assignee',
        required=True,
        help='New assignee in format "team:<team_id>" or "user:<user_id>"'
    )
    parser.add_argument(
        '--base-url',
        default='https://sentry.io',
        help='Sentry base URL (default: https://sentry.io)'
    )
    parser.add_argument(
        '--no-dry-run',
        action='store_true',
        help='Actually perform the reassignment (default is dry-run mode)'
    )
    
    args = parser.parse_args()
    
    # Validate assignee format
    if not validate_assignee(args.assignee):
        print("Error: Invalid assignee format. Use 'team:<team_id>' or 'user:<user_id>'", 
              file=sys.stderr)
        sys.exit(1)
    
    # Create reassigner instance
    reassigner = SentryIssueReassigner(
        auth_token=args.token,
        org_name=args.org,
        project_name=args.project,
        base_url=args.base_url
    )
    
    # Perform reassignment
    dry_run = not args.no_dry_run
    total, successful = reassigner.reassign_issues(
        query=args.query,
        assignee=args.assignee,
        dry_run=dry_run
    )
    
    # Exit with appropriate status code
    if not dry_run and successful < total:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
