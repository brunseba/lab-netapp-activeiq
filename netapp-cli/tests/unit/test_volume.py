"""Tests for volume management commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock
from netapp_cli.main import cli
from netapp_cli.utils.api_client import NetAppAPIError


class TestVolumeCommands:
    """Tests for volume-related CLI commands."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_config, mock_api_client, click_context):
        """Setup click context for testing."""
        self.runner = CliRunner()
        self.mock_ctx = click_context

    @patch('netapp_cli.commands.volume.NetAppAPIClient')
    def test_list_volumes_success(self, MockClient):
        """Test list volumes - success."""
        mock_client = MockClient.return_value
        mock_client.paginate.return_value = [
            {
                "name": "vol-test",
                "svm": {"name": "svm1"},  # Correct nested structure
                "uuid": "abc123",
                "size": "1TB",
                "state": "online",
                "style": "flexvol"
            }
        ]

        result = self.runner.invoke(cli, ['volume', 'list-volumes', '--svm', 'svm1'], obj=self.mock_ctx.obj)
        assert result.exit_code == 0
        assert "vol-test" in result.output
        # Check the full table output, including nested SVM names
        assert "Svm.Name" in result.output
        assert "svm1" in result.output
        assert "1TB" in result.output

    @patch('netapp_cli.commands.volume.NetAppAPIClient')
    def test_list_volumes_empty(self, MockClient):
        """Test list volumes - no volumes found."""
        mock_client = MockClient.return_value
        mock_client.paginate.return_value = []

        result = self.runner.invoke(cli, ['volume', 'list-volumes', '--svm', 'svm1'], obj=self.mock_ctx.obj)
        assert result.exit_code == 0
        assert "No volumes found matching the criteria" in result.output

    @patch('netapp_cli.commands.volume.NetAppAPIClient')
    def test_list_volumes_api_error(self, MockClient):
        """Test list volumes - API error."""
        mock_client = MockClient.return_value
        mock_client.paginate.side_effect = NetAppAPIError("API Failure")

        result = self.runner.invoke(cli, ['volume', 'list-volumes', '--svm', 'svm1'], obj=self.mock_ctx.obj)
        assert result.exit_code != 0
        assert "API Error" in result.output
