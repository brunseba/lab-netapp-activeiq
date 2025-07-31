"""Shared test fixtures and utilities."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from netapp_cli.utils.config import Config, NetAppConfig
from netapp_cli.utils.api_client import NetAppAPIClient


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file."""
    config_content = """
netapp:
  host: test-cluster.example.com
  username: admin
  password: secret123
  verify_ssl: false
  timeout: 30
  api_version: v1
output:
  format: table
  colors: true
logging:
  level: INFO
  file: netapp-cli.log
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def mock_netapp_config():
    """Mock NetApp configuration."""
    return NetAppConfig(
        host="test-cluster.example.com",
        username="admin",
        password="secret123",
        verify_ssl=False,
        timeout=30,
        api_version="v1"
    )


@pytest.fixture
def mock_config(mock_netapp_config):
    """Mock Config object."""
    config = Mock(spec=Config)
    config.netapp = mock_netapp_config
    config.is_configured.return_value = True
    config.get.return_value = None
    return config


@pytest.fixture
def mock_api_client(mock_netapp_config):
    """Mock API client."""
    with patch('netapp_cli.utils.api_client.requests.Session'):
        client = NetAppAPIClient(mock_netapp_config, verbose=False)
        yield client


@pytest.fixture
def sample_volume_data():
    """Sample volume data for tests."""
    return {
        "uuid": "12345678-1234-5678-9012-123456789012",
        "name": "vol-prod-web-data-001",
        "svm": {"name": "svm1", "uuid": "svm-uuid-123"},
        "size": {"total": 1073741824, "used": 536870912},
        "state": "online",
        "style": "flexvol",
        "type": "rw",
        "aggregates": [{"name": "aggr1", "uuid": "aggr-uuid-123"}],
        "language": "c.utf_8",
        "comment": "Web server data volume"
    }


@pytest.fixture
def sample_volumes_list(sample_volume_data):
    """Sample list of volumes."""
    volume2 = sample_volume_data.copy()
    volume2.update({
        "uuid": "87654321-4321-8765-2109-876543210987",
        "name": "vol-prod-db-logs-002",
        "comment": "Database log volume"
    })
    return {
        "records": [sample_volume_data, volume2],
        "num_records": 2
    }


@pytest.fixture
def sample_api_responses():
    """Common API response samples."""
    return {
        "job_success": {
            "job": {
                "uuid": "job-uuid-123",
                "description": "Volume creation job",
                "state": "COMPLETED"
            }
        },
        "job_running": {
            "uuid": "job-uuid-123",
            "description": "Volume creation job",
            "state": "RUNNING",
            "message": "Creating volume..."
        },
        "job_completed": {
            "uuid": "job-uuid-123",
            "description": "Volume creation job",
            "state": "COMPLETED",
            "message": "Volume created successfully"
        },
        "job_failed": {
            "uuid": "job-uuid-123",
            "description": "Volume creation job",
            "state": "FAILED",
            "message": "Volume creation failed: Insufficient space"
        },
        "cluster_info": {
            "uuid": "cluster-uuid-123",
            "name": "test-cluster",
            "version": {"full": "ONTAP 9.14.1"},
            "nodes": [
                {"uuid": "node1-uuid", "name": "node1"},
                {"uuid": "node2-uuid", "name": "node2"}
            ]
        },
        "error_response": {
            "error": {
                "message": "Volume not found",
                "code": "917504"
            }
        }
    }


@pytest.fixture
def click_context():
    """Mock click context."""
    from click.testing import CliRunner
    runner = CliRunner()

    # Create a mock context object
    ctx = Mock()
    ctx.obj = {
        "config": Mock(),
        "verbose": False,
        "output_format": "table"
    }
    return ctx


@pytest.fixture
def cli_runner():
    """Click test runner."""
    from click.testing import CliRunner
    return CliRunner()


@pytest.fixture
def mock_requests():
    """Mock requests for API testing."""
    with patch('netapp_cli.utils.api_client.requests') as mock_req:
        mock_session = Mock()
        mock_req.Session.return_value = mock_session

        # Default successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_session.request.return_value = mock_response

        yield mock_req, mock_session, mock_response


@pytest.fixture(autouse=True)
def disable_ssl_warnings():
    """Disable SSL warnings during testing."""
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Test data constants
TEST_VOLUME_NAMES = {
    "valid": "vol-prod-web-data-001",
    "invalid_prefix": "volume-prod-web-data-001",
    "invalid_env": "vol-production-web-data-001",
    "invalid_format": "vol_prod_web_data_001"
}

TEST_API_ENDPOINTS = {
    "volumes": "/api/storage/volumes",
    "volume_detail": "/api/storage/volumes/{uuid}",
    "snapshots": "/api/storage/volumes/{uuid}/snapshots",
    "cluster": "/api/cluster",
    "jobs": "/management-server/jobs/{uuid}"
}
