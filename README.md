# Totetech Organization GitHub Workflows

This repository contains reusable GitHub workflows and templates for the Totetech organization.

## Claude Code Review Workflow

Automated code review using Claude AI for pull requests.

### Usage

To use the Claude code review workflow in your repository:

1. Create `.github/workflows/claude-review.yml` in your repository
2. Add the following content:

```yaml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize, ready_for_review, edited]

jobs:
  claude-review:
    uses: totetech/.github/.github/workflows/claude-code-review.yml@main
    with:
      skip_large_prs: true
      max_files: 50
      max_lines: 2000
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

- Organization-level `ANTHROPIC_API_KEY` secret must be configured
- Repositories must have appropriate permissions for the workflow

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