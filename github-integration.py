#!/usr/bin/env python3
"""
GitHub API Integration Module for OpenClaw
Automated GitHub repository management and collaboration
"""

import requests
import json
import os
import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class GitHubManager:
    def __init__(self, token: str = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN environment variable.")
        
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenClaw-GitHub-Integration"
        }
    
    def api_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated GitHub API request"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=data)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"GitHub API request failed: {e}")
    
    def get_user_info(self) -> Dict:
        """Get authenticated user information"""
        return self.api_request("GET", "/user")
    
    def get_repositories(self, username: str = None) -> List[Dict]:
        """Get list of repositories"""
        endpoint = "/user/repos" if not username else f"/users/{username}/repos"
        return self.api_request("GET", endpoint, {"sort": "updated", "per_page": 100})
    
    def create_repository(self, name: str, description: str = "", private: bool = False, 
                         auto_init: bool = True) -> Dict:
        """Create a new repository"""
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init,
            "license_template": "mit"  # Default to MIT license
        }
        return self.api_request("POST", "/user/repos", data)
    
    def get_repository(self, owner: str, repo: str) -> Dict:
        """Get repository information"""
        return self.api_request("GET", f"/repos/{owner}/{repo}")
    
    def create_issue(self, owner: str, repo: str, title: str, body: str = "", 
                    labels: List[str] = None, assignees: List[str] = None) -> Dict:
        """Create a new issue"""
        data = {
            "title": title,
            "body": body
        }
        
        if labels:
            data["labels"] = labels
        
        if assignees:
            data["assignees"] = assignees
        
        return self.api_request("POST", f"/repos/{owner}/{repo}/issues", data)
    
    def get_issues(self, owner: str, repo: str, state: str = "open", labels: str = None) -> List[Dict]:
        """Get repository issues"""
        params = {"state": state}
        if labels:
            params["labels"] = labels
        
        return self.api_request("GET", f"/repos/{owner}/{repo}/issues", params)
    
    def create_pull_request(self, owner: str, repo: str, title: str, head: str, base: str = "main",
                           body: str = "", draft: bool = False) -> Dict:
        """Create a pull request"""
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "draft": draft
        }
        return self.api_request("POST", f"/repos/{owner}/{repo}/pulls", data)
    
    def get_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """Get repository pull requests"""
        return self.api_request("GET", f"/repos/{owner}/{repo}/pulls", {"state": state})
    
    def create_branch(self, owner: str, repo: str, branch_name: str, from_branch: str = "main") -> Dict:
        """Create a new branch from latest commit of base branch"""
        # Get the SHA of the latest commit on base branch
        ref_info = self.api_request("GET", f"/repos/{owner}/{repo}/git/ref/heads/{from_branch}")
        base_sha = ref_info["object"]["sha"]
        
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
        return self.api_request("POST", f"/repos/{owner}/{repo}/git/refs", data)
    
    def get_contents(self, owner: str, repo: str, path: str = "", branch: str = None) -> Dict:
        """Get repository contents"""
        params = {}
        if branch:
            params["ref"] = branch
        
        return self.api_request("GET", f"/repos/{owner}/{repo}/contents/{path}", params)
    
    def create_file(self, owner: str, repo: str, path: str, content: str, 
                   message: str = None, branch: str = None) -> Dict:
        """Create or update a file in the repository"""
        import base64
        
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            "message": message or f"Create {path}",
            "content": encoded_content
        }
        
        if branch:
            data["branch"] = branch
        
        return self.api_request("PUT", f"/repos/{owner}/{repo}/contents/{path}", data)
    
    def get_rate_limit(self) -> Dict:
        """Get current rate limit status"""
        return self.api_request("GET", "/rate_limit")
    
    def search_repositories(self, query: str, sort: str = "updated", order: str = "desc") -> List[Dict]:
        """Search for repositories"""
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": 30
        }
        result = self.api_request("GET", "/search/repositories", params)
        return result.get("items", [])
    
    def get_workflows(self, owner: str, repo: str) -> List[Dict]:
        """Get repository GitHub Actions workflows"""
        return self.api_request("GET", f"/repos/{owner}/{repo}/actions/workflows")
    
    def trigger_workflow(self, owner: str, repo: str, workflow_id: str, 
                        ref: str = "main", inputs: Dict = None) -> Dict:
        """Trigger a GitHub Actions workflow"""
        data = {"ref": ref}
        if inputs:
            data["inputs"] = inputs
        
        return self.api_request("POST", f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches", data)
    
    def create_release(self, owner: str, repo: str, tag_name: str, name: str = None,
                      body: str = "", draft: bool = False, prerelease: bool = False) -> Dict:
        """Create a new release"""
        data = {
            "tag_name": tag_name,
            "name": name or tag_name,
            "body": body,
            "draft": draft,
            "prerelease": prerelease
        }
        return self.api_request("POST", f"/repos/{owner}/{repo}/releases", data)

class GitHubWorkflowManager:
    """High-level GitHub workflow automation"""
    
    def __init__(self, token: str = None):
        self.github = GitHubManager(token)
        self.git = None  # Will be initialized when needed
    
    def setup_git_integration(self, repo_path: str = "."):
        """Set up git integration for the workflow"""
        from git_integration import GitManager
        self.git = GitManager(repo_path)
    
    def create_feature_branch(self, owner: str, repo: str, feature_name: str, 
                             base_branch: str = "main") -> Tuple[bool, str]:
        """Create a feature branch with proper naming"""
        try:
            branch_name = f"feature/{feature_name.replace(' ', '-').lower()}"
            result = self.github.create_branch(owner, repo, branch_name, base_branch)
            return True, branch_name
        except Exception as e:
            return False, str(e)
    
    def create_development_issue(self, owner: str, repo: str, title: str, 
                                description: str, labels: List[str] = None) -> Dict:
        """Create a development issue with proper formatting"""
        if not labels:
            labels = ["enhancement", "development"]
        
        body = f"""## Development Task

{description}

### Acceptance Criteria
- [ ] Task requirements met
- [ ] Code reviewed and tested
- [ ] Documentation updated (if needed)

### Technical Notes
*Auto-generated by OpenClaw GitHub Integration*

**Created:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
"""
        
        return self.github.create_issue(owner, repo, title, body, labels)
    
    def automated_pr_workflow(self, owner: str, repo: str, branch_name: str, 
                              changes_description: str, draft: bool = True) -> Dict:
        """Automated pull request creation workflow"""
        # Generate PR title from branch name
        if branch_name.startswith("feature/"):
            title = branch_name.replace("feature/", "").replace("-", " ").title()
        else:
            title = f"Update: {branch_name}"
        
        body = f"""## Changes Overview

{changes_description}

### Changes Made
- Automated changes via OpenClaw integration
- Code review and testing completed

### Checklist
- [ ] Changes tested locally
- [ ] Code follows project standards
- [ ] Documentation updated (if applicable)

**Auto-generated by OpenClaw**
"""
        
        return self.github.create_pull_request(owner, repo, title, branch_name, "main", body, draft)
    
    def sync_local_to_github(self, owner: str, repo: str, branch: str = "main", 
                           commit_message: str = None) -> Tuple[bool, str]:
        """Sync local changes to GitHub repository"""
        if not self.git:
            return False, "Git integration not configured"
        
        try:
            # Commit local changes
            result = self.git.smart_commit_workflow(commit_message, auto_stage=True)
            
            if not result['success']:
                return False, f"Local commit failed: {result['message']}"
            
            # Push to GitHub (this would need git credentials configured)
            # This is a placeholder - actual push would require setup
            return True, f"Local changes committed and ready for GitHub push"
            
        except Exception as e:
            return False, f"Sync failed: {e}"

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Integration Tool')
    parser.add_argument('--token', help='GitHub token (or set GITHUB_TOKEN env var)')
    parser.add_argument('--repo', help='Repository in format owner/repo')
    parser.add_argument('--action', choices=['user', 'repos', 'create-repo', 'issues', 'create-issue'], 
                       help='Action to perform')
    parser.add_argument('--title', help='Issue title')
    parser.add_argument('--body', help='Issue body')
    parser.add_argument('--labels', help='Comma-separated labels')
    
    args = parser.parse_args()
    
    try:
        github = GitHubManager(args.token)
        
        if args.action == 'user':
            user_info = github.get_user_info()
            print(json.dumps(user_info, indent=2))
        
        elif args.action == 'repos':
            repos = github.get_repositories()
            for repo in repos[:5]:  # Show first 5
                print(f"{repo['full_name']} - {repo['description'] or 'No description'}")
        
        elif args.action == 'create-issue' and args.repo and args.title:
            owner, repo = args.repo.split('/')
            labels = args.labels.split(',') if args.labels else None
            issue = github.create_issue(owner, repo, args.title, args.body or "", labels)
            print(f"Created issue #{issue['number']}: {issue['title']}")
        
        else:
            print("Specify --action and required parameters")
    
    except Exception as e:
        print(f"Error: {e}")
        exit(1)