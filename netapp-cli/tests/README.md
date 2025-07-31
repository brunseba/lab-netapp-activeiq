# NetApp CLI Test Suite

This directory contains comprehensive unit and integration tests for the NetApp CLI tool.

## Test Structure

```
tests/
├── __init__.py                    # Test package
├── conftest.py                    # Shared fixtures and utilities
├── pytest.ini                    # Pytest configuration
├── unit/                          # Unit tests
│   ├── __init__.py
│   ├── test_api_client.py        # API client tests
│   ├── test_config.py            # Configuration management tests
│   ├── test_naming.py            # Naming convention tests
│   └── test_volume.py            # Volume command tests
├── integration/                   # Integration tests
│   ├── __init__.py
│   └── test_cli_integration.py   # End-to-end CLI tests
└── fixtures/                     # Test data and fixtures
```

## Running Tests

### Unit Tests

Run all unit tests:

```bash
pytest tests/unit/ -v
```

Run specific test file:

```bash
pytest tests/unit/test_config.py -v
```

Run tests with coverage:

```bash
pytest tests/unit/ --cov=netapp_cli --cov-report=html
```

### Integration Tests

Integration tests require real NetApp cluster credentials:

```bash
export NETAPP_HOST="your-cluster.example.com"
export NETAPP_USERNAME="admin"
export NETAPP_PASSWORD="your-password"

pytest tests/integration/ -v -m integration
```

### Test Markers

The test suite uses markers to categorize tests:

- `unit`: Unit tests (default)
- `integration`: Integration tests requiring real infrastructure
- `slow`: Tests that take longer to run
- `api`: Tests that make API calls
- `config`: Configuration-related tests

Run tests by marker:

```bash
pytest -m "unit and not slow"        # Fast unit tests only
pytest -m "integration and api"      # Integration API tests
pytest -m "not slow"                 # Skip slow tests
```

## Test Coverage

Current test coverage includes:

### ✅ Unit Tests (57 tests)

**Configuration Management (15 tests)**

- Configuration file loading and parsing
- Environment variable overrides
- YAML validation and error handling
- Configuration file search paths
- Sample configuration generation

**API Client (21 tests)**

- HTTP request methods (GET, POST, PATCH, DELETE)
- Authentication header setup
- Error handling and extraction
- Request/response processing
- Job polling and pagination
- SSL warning management
- Connection testing

**Naming Convention (18 tests)**

- Valid/invalid naming patterns
- Environment validation
- Prefix validation
- Complex naming scenarios
- Edge cases and error handling

**Command Interface (3 tests)**

- Volume listing commands
- API error propagation
- Output formatting

### 🚧 Integration Tests (Template)

- CLI command execution
- End-to-end workflows
- Real API interaction testing

## Test Fixtures

The `conftest.py` file provides shared fixtures:

- `temp_config_file`: Temporary configuration file
- `mock_netapp_config`: Mock NetApp configuration
- `mock_config`: Mock Config object
- `mock_api_client`: Mock API client
- `sample_volume_data`: Sample API response data
- `cli_runner`: Click CLI test runner
- `mock_requests`: Mock HTTP requests

## Adding New Tests

### Unit Test Example

```python
# tests/unit/test_my_module.py
import pytest
from netapp_cli.my_module import MyClass

class TestMyClass:
    def test_my_method(self, mock_config):
        """Test my method works correctly."""
        obj = MyClass(mock_config)
        result = obj.my_method("test")
        assert result == "expected"
```

### Integration Test Example

```python
# tests/integration/test_my_integration.py
import pytest
from netapp_cli.main import cli

@pytest.mark.integration
class TestMyIntegration:
    def test_my_command(self, cli_runner):
        """Test my command end-to-end."""
        result = cli_runner.invoke(cli, ['my', 'command'])
        assert result.exit_code == 0
```

## Continuous Integration

Tests are designed to run in CI/CD environments:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    pytest tests/unit/ -v --cov=netapp_cli
    pytest tests/integration/ -v -m "not slow"
```

## Test Configuration

Pytest configuration in `pytest.ini`:

- Verbose output by default
- Colored output
- Warning suppression
- Custom markers
- Test discovery patterns

## Dependencies

Test dependencies are defined in `pyproject.toml`:

- `pytest`: Test framework
- `pytest-mock`: Mocking utilities
- `pytest-cov`: Coverage reporting
- `pytest-xdist`: Parallel test execution

## Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies (API calls, file system)
3. **Fixtures**: Use shared fixtures for common test data
4. **Markers**: Tag tests appropriately for selective execution
5. **Coverage**: Aim for high test coverage of critical paths
6. **Documentation**: Document complex test scenarios

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the CLI package is installed in development mode:

   ```bash
   pip install -e ".[dev]"
   ```

2. **SSL Warnings**: Tests automatically disable SSL warnings during execution

3. **Environment Variables**: Unit tests should not depend on environment variables

4. **Mocking**: Ensure proper mocking of external dependencies to avoid real API calls

For questions or issues with the test suite, please check the existing test implementations for examples.
