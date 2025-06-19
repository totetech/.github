# Workflow Testing

This directory contains comprehensive tests for the Claude code review workflow and other GitHub workflows.

## Test Structure

### 1. Automated Tests (`test-workflows.yml`)

Runs automatically on every push and PR to validate:

- **YAML Syntax Validation**: Ensures all workflow files are valid YAML
- **Required Components**: Verifies workflow_call triggers, permissions, and API keys
- **PR Size Calculation**: Tests the logic for determining PR sizes
- **Input Validation**: Tests different workflow input configurations
- **Size Labeling**: Validates the PR size labeling algorithm (XS/S/M/L)

### 2. Integration Tests (`integration-tests.yml`)

Manual workflow dispatch tests for different scenarios:

- **Small PR Scenario**: Tests workflow with PRs under size limits
- **Large PR Scenario**: Tests workflow with PRs over size limits  
- **Draft PR Scenario**: Tests workflow behavior with draft PRs
- **Custom Prompt Scenario**: Tests custom prompt functionality
- **Comment Collapsing**: Tests the logic for collapsing previous reviews

## Running Tests

### Automatic Tests
Tests run automatically on:
- Push to `main` branch
- Pull requests to `main` branch

### Manual Integration Tests
1. Go to Actions tab in GitHub
2. Select "Integration Tests" workflow
3. Click "Run workflow"
4. Choose test scenario:
   - `all` - Run all integration tests
   - `small-pr` - Test small PR handling
   - `large-pr` - Test large PR handling
   - `draft-pr` - Test draft PR conditions
   - `custom-prompt` - Test custom prompt functionality

## Test Scenarios

### Small PR Test
- **Setup**: Creates 5 JavaScript files with 10 lines each (50 total lines)
- **Expected**: Should trigger Claude review (under limits)
- **Validates**: PR size calculation and review triggering

### Large PR Test  
- **Setup**: Creates 60 JavaScript files with 40+ lines each (3000+ total lines)
- **Expected**: Should skip Claude review (over limits)
- **Validates**: Large PR detection and skip logic

### Draft PR Test
- **Setup**: Simulates draft PR conditions
- **Expected**: Should skip review for draft PRs
- **Validates**: Draft PR condition logic

### Custom Prompt Test
- **Setup**: Tests both empty and custom prompts
- **Expected**: Uses default when empty, custom when provided
- **Validates**: Prompt selection logic

### Comment Collapsing Test
- **Setup**: Mock GitHub comments with different formats
- **Expected**: Identifies and collapses previous Claude reviews
- **Validates**: Comment identification and collapsing logic

## Test Data

Tests use realistic mock data:
- JavaScript files with proper syntax
- Realistic PR sizes and scenarios
- Mock GitHub API responses
- Various workflow configurations

## Continuous Integration

The test suite ensures:
- ✅ Workflow syntax is always valid
- ✅ All required components are present
- ✅ Logic handles edge cases correctly
- ✅ Different configurations work as expected
- ✅ Integration scenarios work end-to-end

## Adding New Tests

To add new test scenarios:

1. **Unit Tests**: Add to `test-workflows.yml`
2. **Integration Tests**: Add to `integration-tests.yml`
3. **Update Documentation**: Document new test cases here

### Example: Adding a New Test Case

```yaml
test-new-scenario:
  runs-on: ubuntu-latest
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Test new scenario
      run: |
        # Your test logic here
        echo "Testing new scenario..."
```