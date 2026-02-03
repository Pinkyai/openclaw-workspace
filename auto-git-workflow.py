#!/usr/bin/env python3
"""
Automated Git Workflow for AI Trading Platform
Handles commits, pushes, and GitHub integration
"""

import subprocess
import json
import os
from datetime import datetime
from pathlib import Path

class AutoGitWorkflow:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path).resolve()
        self.repo_name = "ai-trading-platform"
        self.github_username = "Pinkyai"
        
    def check_git_status(self):
        """Check current git status"""
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd=self.repo_path)
        
        files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        files = [f for f in files if f]  # Remove empty strings
        
        return {
            'has_changes': bool(files),
            'files_changed': len(files),
            'files': files
        }
    
    def get_current_branch(self):
        """Get current git branch"""
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, cwd=self.repo_path)
        return result.stdout.strip()
    
    
    def stage_all_changes(self):
        """Stage all changes"""
        result = subprocess.run(['git', 'add', '.'], 
                              capture_output=True, cwd=self.repo_path)
        return result.returncode == 0
    
    def generate_smart_commit_message(self, status_info):
        """Generate intelligent commit message based on changes"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # Analyze file types
        file_types = {}
        for file_info in status_info['files']:
            status = file_info[:2].strip()
            filename = file_info[3:]
            ext = Path(filename).suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        # Determine action based on file types
        if '.py' in file_types:
            action = "Python development"
        elif any(ext in file_types for ext in ['.html', '.css', '.js']):
            action = "Frontend updates"
        elif '.md' in file_types:
            action = "Documentation updates"
        elif file_types.get('', 0) > 0:  # No extension
            action = "Configuration updates"
        else:
            action = "Workspace updates"
        
        # Add file count
        file_count = status_info['files_changed']
        if file_count == 1:
            files_desc = "1 file"
        else:
            files_desc = f"{file_count} files"
        
        return f"{action}: {files_desc} ({timestamp})"
    
    def commit_changes(self, message):
        """Commit changes with given message"""
        result = subprocess.run(['git', 'commit', '-m', message], 
                              capture_output=True, text=True, cwd=self.repo_path)
        
        if result.returncode == 0:
            # Get commit hash
            hash_result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                       capture_output=True, text=True, cwd=self.repo_path)
            commit_hash = hash_result.stdout.strip()[:7]
            return True, commit_hash
        else:
            return False, result.stderr
    
    def push_to_github(self, branch=None):
        """Push changes to GitHub"""
        if not branch:
            branch = self.get_current_branch()
        
        # Try with SSH first
        result = subprocess.run(['git', 'push', 'origin', branch], 
                              capture_output=True, text=True, cwd=self.repo_path)
        
        if result.returncode == 0:
            return True, f"Successfully pushed to origin/{branch}"
        else:
            # SSH might fail, return error for manual handling
            return False, result.stderr
    
    def run_automated_workflow(self, auto_push=False):
        """Run complete automated workflow"""
        print("🐙 Running automated git workflow...")
        
        # Check status
        status = self.check_git_status()
        print(f"📊 Status: {status['files_changed']} files changed")
        
        if not status['has_changes']:
            print("✨ No changes to commit")
            return {'success': True, 'action': 'none', 'message': 'No changes detected'}
        
        # Stage changes
        if self.stage_all_changes():
            print("✅ Staged all changes")
        else:
            return {'success': False, 'action': 'stage_failed', 'message': 'Failed to stage changes'}
        
        # Generate commit message
        commit_msg = self.generate_smart_commit_message(status)
        print(f"🤖 Generated commit: {commit_msg}")
        
        # Commit
        success, commit_info = self.commit_changes(commit_msg)
        if success:
            print(f"✅ Committed: {commit_msg} ({commit_info})")
        else:
            return {'success': False, 'action': 'commit_failed', 'message': f'Commit failed: {commit_info}'}
        
        # Push if requested
        push_result = None
        if auto_push:
            push_success, push_msg = self.push_to_github()
            if push_success:
                print(f"✅ {push_msg}")
                push_result = 'success'
            else:
                print(f"⚠️  Push failed (manual push needed): {push_msg}")
                push_result = 'manual_needed'
        
        return {
            'success': True, 
            'action': 'committed_and_pushed' if auto_push else 'committed',
            'message': commit_msg,
            'commit_hash': commit_info,
            'files_changed': status['files_changed'],
            'push_result': push_result
        }
    
    def create_daily_summary(self):
        """Create daily summary of git activity"""
        # Get recent commits
        result = subprocess.run(['git', 'log', '--oneline', '-10'], 
                              capture_output=True, text=True, cwd=self.repo_path)
        
        recent_commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'current_branch': self.get_current_branch(),
            'recent_commits': recent_commits,
            'uncommitted_changes': self.check_git_status()['files_changed']
        }
        
        return summary

if __name__ == "__main__":
    import sys
    
    workflow = AutoGitWorkflow()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            status = workflow.check_git_status()
            print(json.dumps(status, indent=2))
        elif sys.argv[1] == "--commit":
            result = workflow.run_automated_workflow(auto_push=False)
            print(json.dumps(result, indent=2))
        elif sys.argv[1] == "--push":
            success, message = workflow.push_to_github()
            print(f"{'✅' if success else '❌'} {message}")
        elif sys.argv[1] == "--summary":
            summary = workflow.create_daily_summary()
            print(json.dumps(summary, indent=2))
        else:
            print("Usage: python3 auto-git-workflow.py [--status|--commit|--push|--summary]")
    else:
        # Run default workflow
        result = workflow.run_automated_workflow(auto_push=False)
        print(json.dumps(result, indent=2))