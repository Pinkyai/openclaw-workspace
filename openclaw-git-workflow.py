#!/usr/bin/env python3
"""
OpenClaw Git/GitHub Workflow Manager
Integrated version control with AI-powered automation
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import our custom modules
import sys
sys.path.append('.')
# Import our custom modules - remove .py extension
exec(open('git-integration.py').read())
exec(open('github-integration.py').read())

class OpenClawGitWorkflow:
    def __init__(self, repo_path: str = ".", github_token: str = None):
        self.repo_path = Path(repo_path).resolve()
        self.git = GitManager(repo_path)
        self.github = GitHubWorkflowManager(github_token) if github_token else None
        self.config_file = self.repo_path / ".openclaw-git.json"
        self.load_config()
    
    def load_config(self):
        """Load workflow configuration"""
        default_config = {
            "auto_commit": True,
            "commit_message_template": "{action}: {summary}",
            "default_branch": "main",
            "github_integration": False,
            "repo_owner": None,
            "repo_name": None,
            "create_issues": True,
            "draft_prs": True,
            "ai_commit_messages": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config = {**default_config, **loaded_config}
            except json.JSONDecodeError:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save workflow configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_github_integration(self, owner: str, repo: str, token: str = None):
        """Set up GitHub integration"""
        if token:
            self.github = GitHubWorkflowManager(token)
        
        self.config.update({
            "github_integration": True,
            "repo_owner": owner,
            "repo_name": repo
        })
        self.save_config()
        
        # Test connection
        try:
            repo_info = self.github.github.get_repository(owner, repo)
            print(f"✅ Connected to GitHub repository: {repo_info['full_name']}")
            return True
        except Exception as e:
            print(f"❌ GitHub connection failed: {e}")
            return False
    
    def smart_workflow_commit(self, action_description: str = None, 
                            files: List[str] = None, auto_push: bool = False) -> Dict:
        """Intelligent commit workflow with AI-powered messages"""
        result = {
            "success": False,
            "commit_hash": None,
            "message": "",
            "files_changed": 0,
            "github_sync": False
        }
        
        # Get current status
        status = self.git.get_status()
        
        if not status['has_changes']:
            result["message"] = "No changes detected"
            return result
        
        # Stage files
        if files:
            success = self.git.stage_specific(files)
        else:
            success = self.git.stage_all()
        
        if not success:
            result["message"] = "Failed to stage files"
            return result
        
        # Generate intelligent commit message
        if action_description:
            commit_message = f"{action_description}"
        else:
            diff_summary = self.git.get_diff_summary()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Analyze what type of changes
            if len(status['staged']) > 5:
                action = "Multiple updates"
            elif any('trading' in str(f).lower() for f in status['staged']):
                action = "Trading platform updates"
            elif any('task' in str(f).lower() for f in status['staged']):
                action = "Task management improvements"
            elif any(f.endswith('.html') or f.endswith('.css') or f.endswith('.js') for f in status['staged']):
                action = "UI/UX improvements"
            else:
                action = "Project updates"
            
            commit_message = f"{action}: {diff_summary['summary']} ({timestamp})"
        
        # Create commit
        success, message = self.git.commit(commit_message, stage_all=False)
        
        if success:
            result["success"] = True
            result["message"] = message
            result["files_changed"] = len(status['staged'])
            
            # Get commit hash
            history = self.git.get_commit_history(1)
            if history:
                result["commit_hash"] = history[0]['hash']
            
            # GitHub sync if enabled
            if self.config["github_integration"] and auto_push:
                github_result = self.sync_to_github()
                result["github_sync"] = github_result["success"]
                result["message"] += f" | {github_result['message']}"
        else:
            result["message"] = f"Commit failed: {message}"
        
        return result
    
    def create_feature_branch(self, feature_name: str, base_branch: str = None) -> Dict:
        """Create a feature branch with proper naming"""
        result = {
            "success": False,
            "branch_name": None,
            "message": ""
        }
        
        # Generate proper branch name
        branch_name = f"feature/{feature_name.replace(' ', '-').lower()}"
        base = base_branch or self.config["default_branch"]
        
        try:
            # Create branch locally
            success = self.git.create_branch(branch_name, checkout=True)
            
            if success:
                result["success"] = True
                result["branch_name"] = branch_name
                result["message"] = f"Created and switched to branch '{branch_name}'"
                
                # Create GitHub branch if integration enabled
                if self.config["github_integration"] and self.config["repo_owner"] and self.config["repo_name"]:
                    try:
                        github_success, github_branch = self.github.create_feature_branch(
                            self.config["repo_owner"],
                            self.config["repo_name"], 
                            feature_name,
                            base
                        )
                        
                        if github_success:
                            result["message"] += f" | GitHub branch '{github_branch}' created"
                        else:
                            result["message"] += f" | GitHub branch creation failed: {github_branch}"
                    except Exception as e:
                        result["message"] += f" | GitHub integration error: {e}"
            else:
                result["message"] = f"Failed to create branch '{branch_name}'"
                
        except Exception as e:
            result["message"] = f"Branch creation failed: {e}"
        
        return result
    
    def create_development_issue(self, title: str, description: str, 
                               labels: List[str] = None) -> Dict:
        """Create a development issue with proper formatting"""
        result = {
            "success": False,
            "issue_number": None,
            "issue_url": None,
            "message": ""
        }
        
        if not self.config["github_integration"]:
            result["message"] = "GitHub integration not configured"
            return result
        
        if not self.config["repo_owner"] or not self.config["repo_name"]:
            result["message"] = "Repository owner/name not configured"
            return result
        
        try:
            issue = self.github.create_development_issue(
                self.config["repo_owner"],
                self.config["repo_name"],
                title,
                description,
                labels
            )
            
            result["success"] = True
            result["issue_number"] = issue["number"]
            result["issue_url"] = issue["html_url"]
            result["message"] = f"Created issue #{issue['number']}: {issue['title']}"
            
        except Exception as e:
            result["message"] = f"Issue creation failed: {e}"
        
        return result
    
    def sync_to_github(self, branch: str = None) -> Dict:
        """Sync local changes to GitHub"""
        result = {
            "success": False,
            "message": ""
        }
        
        if not self.config["github_integration"]:
            result["message"] = "GitHub integration not configured"
            return result
        
        # This would require git credentials to be set up
        # For now, we'll prepare the sync but note it needs manual push
        try:
            branch_info = self.git.get_branch_info()
            current_branch = branch_info['current']
            
            result["success"] = True
            result["message"] = f"Local changes committed on branch '{current_branch}'. Ready for GitHub push."
            result["branch"] = current_branch
            result["needs_manual_push"] = True
            
            # Add instructions for manual push
            result["push_command"] = f"git push origin {current_branch}"
            
        except Exception as e:
            result["message"] = f"Sync preparation failed: {e}"
        
        return result
    
    def get_workflow_summary(self) -> Dict:
        """Get comprehensive workflow summary"""
        try:
            status = self.git.get_status()
            branch_info = self.git.get_branch_info()
            recent_commits = self.git.get_commit_history(5)
            
            return {
                "current_branch": branch_info['current'],
                "has_changes": status['has_changes'],
                "staged_files": len(status['staged']),
                "unstaged_files": len(status['unstaged']),
                "untracked_files": len(status['untracked']),
                "recent_commits": recent_commits,
                "github_integration": self.config['github_integration'],
                "repo_configured": bool(self.config.get('repo_owner') and self.config.get('repo_name'))
            }
        except Exception as e:
            return {
                "error": str(e),
                "github_integration": self.config['github_integration']
            }
    
    def interactive_workflow(self):
        """Interactive workflow for manual control"""
        print("🐙 OpenClaw Git/GitHub Workflow Manager")
        print("=" * 40)
        
        while True:
            print("\nOptions:")
            print("1. Show workflow summary")
            print("2. Smart commit with AI message")
            print("3. Create feature branch")
            print("4. Create GitHub issue")
            print("5. Configure GitHub integration")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                summary = self.get_workflow_summary()
                print(f"\n📊 Workflow Summary:")
                print(json.dumps(summary, indent=2))
            
            elif choice == "2":
                custom_msg = input("Custom commit message (or press Enter for AI generation): ").strip()
                result = self.smart_workflow_commit(custom_msg if custom_msg else None)
                print(f"\n{'✅' if result['success'] else '❌'} {result['message']}")
            
            elif choice == "3":
                feature_name = input("Feature name: ").strip()
                result = self.create_feature_branch(feature_name)
                print(f"\n{'✅' if result['success'] else '❌'} {result['message']}")
            
            elif choice == "4":
                if not self.config["github_integration"]:
                    print("❌ GitHub integration not configured. Use option 5 first.")
                    continue
                
                title = input("Issue title: ").strip()
                description = input("Issue description: ").strip()
                labels_input = input("Labels (comma-separated, optional): ").strip()
                labels = [l.strip() for l in labels_input.split(",")] if labels_input else None
                
                result = self.create_development_issue(title, description, labels)
                print(f"\n{'✅' if result['success'] else '❌'} {result['message']}")
                if result['success']:
                    print(f"🔗 Issue URL: {result['issue_url']}")
            
            elif choice == "5":
                token = input("GitHub token: ").strip()
                owner_repo = input("Repository (owner/repo format): ").strip()
                
                if "/" not in owner_repo:
                    print("❌ Invalid format. Use: owner/repo")
                    continue
                
                owner, repo = owner_repo.split("/", 1)
                success = self.setup_github_integration(owner, repo, token)
                print(f"\n{'✅' if success else '❌'} GitHub integration setup complete")
            
            elif choice == "6":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid option. Please select 1-6.")

# Quick test function
def test_workflow():
    """Test the workflow with current repository"""
    print("🧪 Testing OpenClaw Git Workflow...")
    
    workflow = OpenClawGitWorkflow()
    
    # Show current status
    summary = workflow.get_workflow_summary()
    print(f"📊 Current Status:")
    print(f"   Branch: {summary['current_branch']}")
    print(f"   Changes: {summary['has_changes']}")
    print(f"   Staged: {summary['staged_files']}")
    print(f"   Unstaged: {summary['unstaged_files']}")
    
    # Test smart commit
    if summary['has_changes']:
        print(f"\n🤖 Creating smart commit...")
        result = workflow.smart_workflow_commit("Test automated commit workflow")
        print(f"{'✅' if result['success'] else '❌'} {result['message']}")
    else:
        print("\n✨ No changes to commit - everything looks good!")
    
    return workflow

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_workflow()
    elif len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        workflow = OpenClawGitWorkflow()
        workflow.interactive_workflow()
    else:
        print("🐙 OpenClaw Git/GitHub Workflow Manager")
        print("Usage:")
        print("  python3 openclaw-git-workflow.py --test      # Run quick test")
        print("  python3 openclaw-git-workflow.py --interactive  # Interactive mode")