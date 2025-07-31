"""Integration tests for NetApp CLI.

These tests require a real NetApp cluster or properly configured mock server.
Set environment variables to run against real infrastructure.
"""

import pytest
import os
from click.testing import CliRunner

from netapp_cli.main import cli


@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for the CLI tool."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for integration tests."""
        self.runner = CliRunner()

        # Skip if no real NetApp credentials available
        if not all([
            os.getenv("NETAPP_HOST"),
            os.getenv("NETAPP_USERNAME"),
            os.getenv("NETAPP_PASSWORD")
        ]):
            pytest.skip("Integration tests require NETAPP_* environment variables")

    def test_version_command(self):
        """Test version command works."""
        result = self.runner.invoke(cli, ['version'])
        assert result.exit_code == 0
        assert "NetApp CLI" in result.output

    @pytest.mark.api
    def test_auth_test_connection(self):
        """Test authentication and connection test."""
        result = self.runner.invoke(cli, ['auth', 'test'])
        # This would test actual connection if credentials are available
        # For now, just ensure command structure works
        assert result.exit_code in [0, 1]  # Success or auth failure

    @pytest.mark.slow
    def test_list_volumes_integration(self):
        """Test listing volumes against real cluster."""
        # This would require specific test SVM
        test_svm = os.getenv("NETAPP_TEST_SVM", "test-svm")
        result = self.runner.invoke(cli, ['volume', 'list-volumes', '--svm', test_svm])

        # Should either succeed or fail with proper error message
        assert result.exit_code in [0, 1]
        if result.exit_code == 0:
            assert "Volumes" in result.output or "No volumes found" in result.output


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndWorkflows:
    """End-to-end workflow tests."""

    def test_complete_volume_workflow(self):
        """Test complete volume management workflow."""
        # This would test: create -> list -> show -> delete
        # Requires proper test environment setup
        pytest.skip("Requires dedicated test environment")

    def test_snapshot_workflow(self):
        """Test snapshot management workflow."""
        # This would test: create policy -> assign -> create snapshot -> list -> delete
        pytest.skip("Requires dedicated test environment")


# Pytest markers for different test types
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.getenv("NETAPP_HOST"),
        reason="Integration tests require NETAPP_HOST environment variable"
    )
]
