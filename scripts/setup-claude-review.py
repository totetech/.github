#!/usr/bin/env python3
"""
Claude Code Review Workflow Setup Script

Automatically implements Claude review workflow in any Totetech repository.

Usage:
    python setup-claude-review.py <repo-name>
    
Example:
    python setup-claude-review.py my-repo
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_colored(message: str, color: str = Colors.NC):
    """Print message with color."""
    print(f"{color}{message}{Colors.NC}")

def run_command(cmd: list, capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    try:
        return subprocess.run(cmd, capture_output=capture_output, text=True, check=check)
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Command failed: {' '.join(cmd)}", Colors.RED)
        print_colored(f"Error: {e.stderr}", Colors.RED)
        raise

def check_prerequisites() -> bool:
    """Check if all prerequisites are met."""
    print_colored("🔍 Checking prerequisites...", Colors.BLUE)
    
    # Check if in git repository
    try:
        run_command(['git', 'rev-parse', '--git-dir'])
        print_colored("✅ Git repository detected", Colors.GREEN)
    except subprocess.CalledProcessError:
        print_colored("❌ Not in a git repository", Colors.RED)
        print_colored("Please run this script from the root of your repository", Colors.RED)
        return False
    
    # Check if GitHub CLI is available
    try:
        run_command(['gh', '--version'])
        print_colored("✅ GitHub CLI available", Colors.GREEN)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_colored("❌ GitHub CLI not found", Colors.RED)
        print_colored("Please install GitHub CLI: https://cli.github.com/", Colors.RED)
        return False
    
    return True

def verify_repository_access(repo_name: str) -> bool:
    """Verify access to the target repository."""
    print_colored(f"🔍 Verifying access to totetech/{repo_name}...", Colors.BLUE)
    
    try:
        run_command(['gh', 'repo', 'view', f'totetech/{repo_name}'])
        print_colored("✅ Repository access verified", Colors.GREEN)
        return True
    except subprocess.CalledProcessError:
        print_colored(f"❌ Cannot access repository totetech/{repo_name}", Colors.RED)
        print_colored("Please ensure:", Colors.RED)
        print_colored("- Repository exists", Colors.RED)
        print_colored("- You have access to the repository", Colors.RED)
        print_colored("- GitHub CLI is authenticated (run 'gh auth login')", Colors.RED)
        return False

def ensure_github_repo_public() -> bool:
    """Ensure the .github repository is public."""
    print_colored("🔍 Checking .github repository visibility...", Colors.BLUE)
    
    try:
        result = run_command(['gh', 'api', 'repos/totetech/.github', '--jq', '.visibility'])
        visibility = result.stdout.strip()
        
        if visibility != 'public':
            print_colored(f"⚠️  .github repository is {visibility}, needs to be public", Colors.YELLOW)
            
            response = input("Make .github repository public? (y/N): ")
            if response.lower() == 'y':
                print_colored("🔧 Making .github repository public...", Colors.BLUE)
                run_command(['gh', 'repo', 'edit', 'totetech/.github', 
                           '--visibility', 'public', '--accept-visibility-change-consequences'])
                print_colored("✅ .github repository is now public", Colors.GREEN)
                return True
            else:
                print_colored("❌ .github repository must be public for reusable workflows", Colors.RED)
                return False
        else:
            print_colored("✅ .github repository is public", Colors.GREEN)
            return True
            
    except subprocess.CalledProcessError:
        print_colored("❌ Failed to check .github repository visibility", Colors.RED)
        return False

def check_anthropic_secret(repo_name: str) -> None:
    """Check for ANTHROPIC_API_KEY secret."""
    print_colored("🔍 Checking for ANTHROPIC_API_KEY secret...", Colors.BLUE)
    
    try:
        result = run_command(['gh', 'secret', 'list', '--repo', f'totetech/{repo_name}'])
        if 'ANTHROPIC_API_KEY' in result.stdout:
            print_colored("✅ ANTHROPIC_API_KEY secret found at repository level", Colors.GREEN)
        else:
            print_colored("⚠️  ANTHROPIC_API_KEY not found at repository level", Colors.YELLOW)
            print_colored("Assuming organization-level secret exists...", Colors.BLUE)
    except subprocess.CalledProcessError:
        print_colored("ℹ️  Could not check secrets, assuming organization-level secret exists", Colors.BLUE)

def handle_legacy_workflow() -> bool:
    """Handle existing claude.yml workflow."""
    legacy_file = Path('.github/workflows/claude.yml')
    
    if legacy_file.exists():
        print_colored("⚠️  Found legacy claude.yml workflow", Colors.YELLOW)
        print_colored("This should be replaced with the new claude-review.yml", Colors.YELLOW)
        
        response = input("Delete legacy claude.yml workflow? (y/N): ")
        if response.lower() == 'y':
            print_colored("🗑️  Removing legacy workflow...", Colors.BLUE)
            legacy_file.unlink()
            print_colored("✅ Legacy workflow removed", Colors.GREEN)
            return True
        else:
            print_colored("⚠️  Legacy workflow kept - you may have duplicate workflows", Colors.YELLOW)
            print_colored("Consider manually removing claude.yml after testing", Colors.YELLOW)
    
    return False

def create_workflow_file() -> None:
    """Create the Claude review workflow file."""
    print_colored("📁 Creating .github/workflows directory...", Colors.BLUE)
    workflows_dir = Path('.github/workflows')
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_file = workflows_dir / 'claude-review.yml'
    
    if workflow_file.exists():
        print_colored("⚠️  claude-review.yml already exists - will overwrite", Colors.YELLOW)
    
    print_colored("📝 Creating Claude review workflow file...", Colors.BLUE)
    
    workflow_content = """name: Claude Code Review
# Automated AI-powered code reviews for pull requests

on:
  pull_request:
    types: [opened, synchronize, ready_for_review, edited]

permissions:
  contents: read
  id-token: write
  pull-requests: write
  issues: write

jobs:
  claude-review:
    uses: totetech/.github/.github/workflows/claude-code-review.yml@main
    with:
      skip_large_prs: true
      max_files: 50
      max_lines: 2000
      # custom_prompt: |
      #   Add your custom review prompt here if needed
      #   This will override the default prompt
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
"""
    
    workflow_file.write_text(workflow_content)
    print_colored("✅ Workflow file created", Colors.GREEN)

def validate_yaml(file_path: Path) -> None:
    """Validate YAML syntax if yamllint is available."""
    print_colored("🔍 Validating YAML syntax...", Colors.BLUE)
    
    try:
        run_command(['yamllint', str(file_path)])
        print_colored("✅ YAML syntax is valid", Colors.GREEN)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_colored("ℹ️  yamllint not available, skipping validation", Colors.BLUE)

def commit_and_push_changes(legacy_removed: bool) -> None:
    """Commit and optionally push the changes."""
    print_colored("📤 Preparing commit...", Colors.BLUE)
    
    # Stage all workflow changes
    run_command(['git', 'add', '.github/workflows/'])
    
    # Check if there are changes to commit
    try:
        run_command(['git', 'diff', '--cached', '--quiet'])
        print_colored("ℹ️  No changes to commit", Colors.BLUE)
        return
    except subprocess.CalledProcessError:
        # There are changes to commit
        pass
    
    # Create commit message
    commit_message = """Add Claude code review workflow

- Implements automated AI-powered code reviews
- Configures size limits: 50 files, 2000 lines
- Includes proper permissions and secrets configuration
- Automatically triggers on PR events"""
    
    if legacy_removed:
        commit_message += "\n- Removes legacy claude.yml workflow"
    
    run_command(['git', 'commit', '-m', commit_message])
    print_colored("✅ Changes committed", Colors.GREEN)
    
    # Ask about pushing
    print()
    response = input("🚀 Push to repository? (y/N): ")
    if response.lower() == 'y':
        print_colored("📤 Pushing to repository...", Colors.BLUE)
        run_command(['git', 'push'])
        print_colored("✅ Changes pushed", Colors.GREEN)
    else:
        print_colored("ℹ️  Changes committed locally. Push when ready: git push", Colors.BLUE)

def print_completion_message(legacy_removed: bool) -> None:
    """Print completion message with next steps."""
    print()
    print_colored("🎉 Claude Code Review Workflow Setup Complete!", Colors.GREEN)
    print()
    print_colored("📋 Next Steps:", Colors.BLUE)
    print("1. 📤 Push changes if not already done: git push")
    print("2. 🔍 Create a test PR to verify the workflow")
    print("3. ✅ Check Actions tab for workflow execution")
    print("4. 💬 Confirm Claude review appears on PR")
    print()
    print_colored("📚 Documentation:", Colors.BLUE)
    print("- Workflow file: .github/workflows/claude-review.yml")
    print("- Configuration: https://github.com/totetech/.github#claude-code-review-workflow")
    print("- Troubleshooting: https://github.com/totetech/.github#troubleshooting")
    print()
    print_colored("⚙️  Current Configuration:", Colors.BLUE)
    print("- Max files: 50")
    print("- Max lines: 2000")
    print("- Skip large PRs: true")
    print("- Triggers: opened, synchronize, ready_for_review, edited")
    print()
    
    if legacy_removed:
        print_colored("🗑️  Legacy Workflow:", Colors.BLUE)
        print("- claude.yml removed (available in git history)")
        print()
    
    print_colored("✨ Happy coding with AI-powered reviews!", Colors.GREEN)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Setup Claude Code Review workflow for Totetech repositories"
    )
    parser.add_argument('repo_name', help='Repository name (without org prefix)')
    args = parser.parse_args()
    
    print_colored("🤖 Claude Code Review Workflow Setup", Colors.BLUE)
    print_colored("======================================", Colors.BLUE)
    print()
    print_colored(f"📋 Setting up Claude review workflow for: totetech/{args.repo_name}", Colors.BLUE)
    print()
    
    try:
        # Check prerequisites
        if not check_prerequisites():
            sys.exit(1)
        
        # Verify repository access
        if not verify_repository_access(args.repo_name):
            sys.exit(1)
        
        # Ensure .github repo is public
        if not ensure_github_repo_public():
            sys.exit(1)
        
        # Check for API key secret
        check_anthropic_secret(args.repo_name)
        
        # Handle legacy workflow
        legacy_removed = handle_legacy_workflow()
        
        # Create new workflow file
        create_workflow_file()
        
        # Validate YAML
        validate_yaml(Path('.github/workflows/claude-review.yml'))
        
        # Commit and push changes
        commit_and_push_changes(legacy_removed)
        
        # Print completion message
        print_completion_message(legacy_removed)
        
    except KeyboardInterrupt:
        print_colored("\n❌ Setup cancelled by user", Colors.RED)
        sys.exit(1)
    except Exception as e:
        print_colored(f"❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)

if __name__ == '__main__':
    main()