#!/usr/bin/env python3
"""
Git Integration Module for OpenClaw
Automated git workflow management with AI-powered commit messages
"""

import subprocess
import json
import os
import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class GitManager:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.ensure_git_repo()
    
    def ensure_git_repo(self):
        """Ensure we're in a git repository"""
        try:
            self.run_git_command(["rev-parse", "--git-dir"], check=True)
        except subprocess.CalledProcessError:
            raise ValueError(f"{self.repo_path} is not a git repository")
    
    def run_git_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command safely"""
        try:
            return subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                check=check,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {e.stderr}")
    
    def get_status(self) -> Dict:
        """Get comprehensive git status"""
        result = self.run_git_command(["status", "--porcelain=v1"])
        
        staged = []
        unstaged = []
        untracked = []
        
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            status = line[:2]
            filename = line[3:]
            
            if status[0] != ' ':
                staged.append({
                    'file': filename,
                    'status': self.interpret_status(status[0])
                })
            
            if status[1] != ' ':
                if status[1] == '?':
                    untracked.append(filename)
                else:
                    unstaged.append({
                        'file': filename,
                        'status': self.interpret_status(status[1])
                    })
        
        return {
            'staged': staged,
            'unstaged': unstaged,
            'untracked': untracked,
            'has_changes': len(staged) > 0 or len(unstaged) > 0 or len(untracked) > 0
        }
    
    def interpret_status(self, status_char: str) -> str:
        """Interpret git status characters"""
        status_map = {
            'M': 'modified',
            'A': 'added',
            'D': 'deleted',
            'R': 'renamed',
            'C': 'copied',
            'U': 'updated',
            '?': 'untracked'
        }
        return status_map.get(status_char, 'unknown')
    
    def get_diff_summary(self) -> str:
        """Get a summary of changes for commit message generation"""
        status = self.get_status()
        if not status['has_changes']:
            return "No changes detected"
        
        summary_parts = []
        
        if status['staged']:
            summary_parts.append(f"Staged: {len(status['staged'])} files")
        
        if status['unstaged']:
            summary_parts.append(f"Modified: {len(status['unstaged'])} files")
        
        if status['untracked']:
            summary_parts.append(f"Untracked: {len(status['untracked'])} files")
        
        # Get file details
        details = []
        for file_info in status['staged']:
            details.append(f"+ {file_info['file']} ({file_info['status']})")
        
        for file_info in status['unstaged']:
            details.append(f"~ {file_info['file']} ({file_info['status']})")
        
        for filename in status['untracked']:
            details.append(f"? {filename} (new)")
        
        return {
            'summary': '; '.join(summary_parts),
            'details': '\n'.join(details[:10])  # Limit to first 10 files
        }
    
    def generate_commit_message(self, custom_message: str = None) -> str:
        """Generate an intelligent commit message"""
        if custom_message:
            return custom_message
        
        diff_summary = self.get_diff_summary()
        if diff_summary == "No changes detected":
            return "No changes to commit"
        
        # Analyze changes and generate meaningful message
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Simple but meaningful message generation
        if "Staged:" in diff_summary['summary']:
            if len(diff_summary['summary'].split(';')) == 1:
                return f"Update: {diff_summary['summary']}"
            else:
                return f"Multiple updates: {diff_summary['summary']}"
        elif "Modified:" in diff_summary['summary']:
            return f"Modify: {diff_summary['summary']}"
        elif "Untracked:" in diff_summary['summary']:
            return f"Add: {diff_summary['summary']}"
        else:
            return f"Update files ({timestamp})"
    
    def stage_all(self) -> bool:
        """Stage all changes (including untracked)"""
        try:
            self.run_git_command(["add", "."])
            return True
        except RuntimeError as e:
            print(f"Failed to stage files: {e}")
            return False
    
    def stage_specific(self, files: List[str]) -> bool:
        """Stage specific files"""
        try:
            for file in files:
                self.run_git_command(["add", file])
            return True
        except RuntimeError as e:
            print(f"Failed to stage files: {e}")
            return False
    
    def commit(self, message: str = None, stage_all: bool = False) -> Tuple[bool, str]:
        """Create a commit with intelligent message generation"""
        status = self.get_status()
        
        if not status['has_changes']:
            return False, "No changes to commit"
        
        # Stage files if requested
        if stage_all:
            if not self.stage_all():
                return False, "Failed to stage files"
        
        # Generate commit message
        commit_message = self.generate_commit_message(message)
        
        try:
            self.run_git_command(["commit", "-m", commit_message])
            return True, f"Committed: {commit_message}"
        except RuntimeError as e:
            return False, f"Commit failed: {e}"
    
    def get_commit_history(self, limit: int = 10) -> List[Dict]:
        """Get recent commit history"""
        try:
            result = self.run_git_command([
                "log", f"-{limit}", "--pretty=format:%H|%an|%ae|%ad|%s",
                "--date=iso"
            ])
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|', 4)
                if len(parts) == 5:
                    commits.append({
                        'hash': parts[0][:8],  # Short hash
                        'author': parts[1],
                        'email': parts[2],
                        'date': parts[3],
                        'message': parts[4]
                    })
            
            return commits
        except RuntimeError:
            return []
    
    def get_branch_info(self) -> Dict:
        """Get current branch information"""
        try:
            # Get current branch
            result = self.run_git_command(["branch", "--show-current"])
            current_branch = result.stdout.strip()
            
            # Get all branches
            result = self.run_git_command(["branch", "-a"])
            branches = [line.strip().replace('* ', '').replace('remotes/', '') 
                       for line in result.stdout.split('\n') if line.strip()]
            
            return {
                'current': current_branch,
                'all': branches
            }
        except RuntimeError:
            return {'current': 'unknown', 'all': []}
    
    def create_branch(self, branch_name: str, checkout: bool = False) -> bool:
        """Create a new branch"""
        try:
            if checkout:
                self.run_git_command(["checkout", "-b", branch_name])
            else:
                self.run_git_command(["branch", branch_name])
            return True
        except RuntimeError as e:
            print(f"Failed to create branch: {e}")
            return False
    
    def smart_commit_workflow(self, custom_message: str = None, auto_stage: bool = True) -> Dict:
        """Intelligent commit workflow with status checking"""
        result = {
            'success': False,
            'message': '',
            'changes_staged': 0,
            'changes_committed': 0
        }
        
        # Get initial status
        status = self.get_status()
        result['initial_status'] = status
        
        if not status['has_changes']:
            result['message'] = "No changes detected"
            return result
        
        # Stage changes if requested
        if auto_stage and status['unstaged']:
            if self.stage_all():
                result['changes_staged'] = len(status['unstaged'])
            else:
                result['message'] = "Failed to stage changes"
                return result
        
        # Commit changes
        success, message = self.commit(custom_message, stage_all=False)
        result['success'] = success
        result['message'] = message
        
        if success:
            # Get final status
            final_status = self.get_status()
            result['final_status'] = final_status
            result['changes_committed'] = len(status['staged']) + result['changes_staged']
        
        return result

# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Git Integration Tool')
    parser.add_argument('--path', default='.', help='Repository path')
    parser.add_argument('--commit', action='store_true', help='Create commit')
    parser.add_argument('--message', help='Commit message')
    parser.add_argument('--stage-all', action='store_true', help='Stage all changes')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--history', action='store_true', help='Show commit history')
    
    args = parser.parse_args()
    
    git_manager = GitManager(args.path)
    
    if args.status:
        status = git_manager.get_status()
        print(json.dumps(status, indent=2))
    elif args.commit:
        result = git_manager.smart_commit_workflow(args.message, args.stage_all)
        print(json.dumps(result, indent=2))
    elif args.history:
        history = git_manager.get_commit_history()
        for commit in history:
            print(f"{commit['hash']} - {commit['message']} ({commit['date']})")
    else:
        status = git_manager.get_status()
        print(f"Repository status: {status['summary']}")
        print(f"Has changes: {status['has_changes']}")