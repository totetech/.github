# Totetech Organization GitHub Workflows

This repository contains reusable GitHub workflows and templates for the Totetech organization.

## Claude Code Review Workflow

Automated code review using Claude AI for pull requests.

### Quick Setup

**One-shot implementation:** Use our automated setup script:

```bash
# Download and run the setup script
curl -sSL https://raw.githubusercontent.com/totetech/.github/main/scripts/setup-claude-review.py | python3 - <repo-name>

# Or clone and run locally
git clone https://github.com/totetech/.github.git
cd .github
python3 scripts/setup-claude-review.py <repo-name>
```

### Manual Setup

To manually implement the Claude code review workflow in your repository:

1. Create `.github/workflows/claude-review.yml` in your repository
2. Add the **complete** configuration below:

```yaml
name: Claude Code Review
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
```

### Configuration Options

| Input | Description | Default |
|-------|-------------|---------|
| `skip_large_prs` | Skip review for large PRs | `true` |
| `max_files` | Maximum files to trigger review | `50` |
| `max_lines` | Maximum lines changed to trigger review | `2000` |
| `custom_prompt` | Custom review prompt (optional) | Default prompt |

### Features

- ✅ Automatic PR size labeling (XS/S/M/L)
- ✅ Skips review for draft PRs and bot PRs
- ✅ Collapses previous review comments
- ✅ Configurable size limits
- ✅ Custom review prompts
- ✅ Skip review with `skip-review` label

### Prerequisites

#### Required Setup
1. **Organization-level secrets:**
   - `ANTHROPIC_API_KEY` must be configured at organization level
   - Available to all repositories in the organization

2. **Repository permissions:**
   - GitHub Actions must be enabled
   - Workflow permissions: Read repository contents and metadata, Write pull requests and issues

3. **Organization `.github` repository:**
   - **MUST be public** for reusable workflows to be accessible
   - Contains the reusable workflow at `.github/workflows/claude-code-review.yml`

#### Critical Requirements
- ✅ **Permissions block** - Required for workflow to access PR data
- ✅ **Secrets block** - Required to pass ANTHROPIC_API_KEY to reusable workflow  
- ✅ **Public .github repo** - Required for cross-repository workflow access
- ✅ **Complete workflow path** - `totetech/.github/.github/workflows/claude-code-review.yml@main`

### Example with Custom Prompt

```yaml
jobs:
  claude-review:
    uses: totetech/.github/.github/workflows/claude-code-review.yml@main
    with:
      custom_prompt: |
        Focus on security vulnerabilities and performance issues.
        Pay special attention to database queries and API endpoints.
```

## Testing

This repository includes comprehensive tests for the Claude code review workflow:

### Automated Tests
- **Syntax Validation**: YAML validation for all workflows
- **Component Validation**: Checks required triggers, permissions, and secrets
- **Logic Testing**: PR size calculation and labeling algorithms
- **Input Validation**: Tests different configuration scenarios

### Integration Tests
Manual workflow dispatch tests for:
- Small PR scenarios (under size limits)
- Large PR scenarios (over size limits)
- Draft PR handling
- Custom prompt functionality
- Comment collapsing logic

### Running Tests
- Automatic tests run on every push/PR
- Integration tests: Actions → "Integration Tests" → "Run workflow"

See [`tests/README.md`](tests/README.md) for detailed testing documentation.

## Troubleshooting

### Common Issues and Solutions

#### 1. "workflow was not found" Error
```
error parsing called workflow: workflow was not found
```
**Cause:** `.github` repository is not public or workflow path is incorrect  
**Solution:** 
- Ensure `totetech/.github` repository is **public**
- Verify path: `totetech/.github/.github/workflows/claude-code-review.yml@main`

#### 2. "invalid value workflow reference" Error  
```
invalid value workflow reference: references to workflows must be prefixed with format 'owner/repository/'
```
**Cause:** Incorrect workflow reference format  
**Solution:** Use exact path `totetech/.github/.github/workflows/claude-code-review.yml@main`

#### 3. Permissions Error
```
The workflow is requesting 'issues: write, pull-requests: write', but is only allowed 'none'
```
**Cause:** Missing permissions block in calling workflow  
**Solution:** Add complete permissions block to your workflow file

#### 4. "ANTHROPIC_API_KEY is required" Error
```
Environment variable validation failed: ANTHROPIC_API_KEY is required
```
**Cause:** Missing secrets configuration  
**Solution:** Add `secrets:` block with `ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}`

#### 5. Workflow doesn't trigger
**Cause:** Missing trigger events or draft PR  
**Solution:** 
- Ensure PR is not in draft mode
- Check trigger events include `[opened, synchronize, ready_for_review, edited]`
- Verify repository has GitHub Actions enabled

### Validation Checklist

Before implementing, verify:
- [ ] Organization has `ANTHROPIC_API_KEY` secret configured
- [ ] `totetech/.github` repository is **public**
- [ ] Repository has GitHub Actions enabled  
- [ ] Workflow file includes all required sections:
  - [ ] `permissions:` block with `contents: read`, `id-token: write`, `pull-requests: write`, `issues: write`
  - [ ] `secrets:` block with `ANTHROPIC_API_KEY`
  - [ ] Correct workflow path reference
  - [ ] Proper trigger events

### Testing Implementation

1. **Create test PR** with small changes (< 50 files, < 2000 lines)
2. **Verify workflow appears** in Actions tab
3. **Check for errors** in workflow run logs
4. **Confirm review comment** appears on PR

### Need Help?

1. **Check workflow runs** in repository Actions tab
2. **Review error logs** for specific failure messages  
3. **Validate configuration** against working example: [`rn-windows-pos`](https://github.com/totetech/rn-windows-pos/blob/main/.github/workflows/claude-review.yml)
4. **Test with minimal PR** to isolate issues