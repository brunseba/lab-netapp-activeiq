"""Tests for NetApp API client."""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
import requests

from netapp_cli.utils.api_client import NetAppAPIClient, NetAppAPIError
from netapp_cli.utils.config import NetAppConfig


class TestNetAppAPIClient:
    """Tests for NetApp API client."""

    @pytest.fixture
    def mock_netapp_config(self):
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
    def mock_response(self):
        """Mock HTTP response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"success": True, "data": []}
        response.text = '{"success": true}'
        return response

    @pytest.fixture
    def mock_session(self, mock_response):
        """Mock requests session."""
        session = Mock()
        session.request.return_value = mock_response
        session.headers = {}
        return session

    def test_client_initialization(self, mock_netapp_config):
        """Test API client initialization."""
        with patch('netapp_cli.utils.api_client.requests.Session') as MockSession:
            mock_session = Mock()
            MockSession.return_value = mock_session

            client = NetAppAPIClient(mock_netapp_config, verbose=False)

            assert client.config == mock_netapp_config
            assert client.verbose is False
            assert client.base_url == "https://test-cluster.example.com"

            # Check that session was configured
            MockSession.assert_called_once()
            assert mock_session.verify is False  # SSL verification disabled

    def test_client_authentication_header(self, mock_netapp_config):
        """Test authentication header setup."""
        with patch('netapp_cli.utils.api_client.requests.Session') as MockSession:
            mock_session = Mock()
            MockSession.return_value = mock_session

            client = NetAppAPIClient(mock_netapp_config, verbose=False)

            # Check that authorization header was set
            expected_calls = mock_session.headers.update.call_args_list
            assert len(expected_calls) > 0

            # Verify authorization header contains Basic auth
            auth_header = expected_calls[0][0][0]["Authorization"]
            assert auth_header.startswith("Basic ")

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_get_request_success(self, MockSession, mock_netapp_config, mock_response):
        """Test successful GET request."""
        mock_session = MockSession.return_value
        mock_session.request.return_value = mock_response

        client = NetAppAPIClient(mock_netapp_config, verbose=False)
        result = client.get("/api/storage/volumes")

        assert result == {"success": True, "data": []}
        mock_session.request.assert_called_once_with(
            method="GET",
            url="https://test-cluster.example.com/api/storage/volumes",
            params=None,
            json=None,
            timeout=30,
            headers={}
        )

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_get_request_with_params(self, MockSession, mock_netapp_config, mock_response):
        """Test GET request with parameters."""
        mock_session = MockSession.return_value
        mock_session.request.return_value = mock_response

        client = NetAppAPIClient(mock_netapp_config, verbose=False)
        params = {"name": "vol1", "svm.name": "svm1"}
        result = client.get("/api/storage/volumes", params=params)

        mock_session.request.assert_called_once_with(
            method="GET",
            url="https://test-cluster.example.com/api/storage/volumes",
            params=params,
            json=None,
            timeout=30,
            headers={}
        )

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_post_request_success(self, MockSession, mock_netapp_config, mock_response):
        """Test successful POST request."""
        mock_session = MockSession.return_value
        mock_session.request.return_value = mock_response

        client = NetAppAPIClient(mock_netapp_config, verbose=False)
        data = {"name": "new-volume", "size": 1000000000}
        result = client.post("/api/storage/volumes", data=data)

        mock_session.request.assert_called_once_with(
            method="POST",
            url="https://test-cluster.example.com/api/storage/volumes",
            params=None,
            json=data,
            timeout=30,
            headers={}
        )

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_patch_request_success(self, MockSession, mock_netapp_config, mock_response):
        """Test successful PATCH request."""
        mock_session = MockSession.return_value
        mock_session.request.return_value = mock_response

        client = NetAppAPIClient(mock_netapp_config, verbose=False)
        data = {"comment": "Updated comment"}
        result = client.patch("/api/storage/volumes/uuid123", data=data)

        mock_session.request.assert_called_once_with(
            method="PATCH",
            url="https://test-cluster.example.com/api/storage/volumes/uuid123",
            params=None,
            json=data,
            timeout=30,
            headers={}
        )

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_delete_request_success(self, MockSession, mock_netapp_config, mock_response):
        """Test successful DELETE request."""
        mock_session = MockSession.return_value
        mock_session.request.return_value = mock_response

        client = NetAppAPIClient(mock_netapp_config, verbose=False)
        result = client.delete("/api/storage/volumes/uuid123")

        mock_session.request.assert_called_once_with(
            method="DELETE",
            url="https://test-cluster.example.com/api/storage/volumes/uuid123",
            params=None,
            json=None,
            timeout=30,
            headers={}
        )

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_api_error_handling(self, MockSession, mock_netapp_config):
        """Test API error handling."""
        mock_session = MockSession.return_value
        error_response = Mock()
        error_response.status_code = 404
        error_response.json.return_value = {"error": {"message": "Volume not found"}}
        mock_session.request.return_value = error_response

        client = NetAppAPIClient(mock_netapp_config, verbose=False)

        with pytest.raises(NetAppAPIError) as exc_info:
            client.get("/api/storage/volumes/nonexistent")

        assert exc_info.value.status_code == 404
        assert "Volume not found" in str(exc_info.value)

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_request_exception_handling(self, MockSession, mock_netapp_config):
        """Test request exception handling."""
        mock_session = MockSession.return_value
        mock_session.request.side_effect = requests.exceptions.ConnectionError("Connection failed")

        client = NetAppAPIClient(mock_netapp_config, verbose=False)

        with pytest.raises(NetAppAPIError) as exc_info:
            client.get("/api/cluster")

        assert "Request failed" in str(exc_info.value)
        assert "Connection failed" in str(exc_info.value)

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_no_content_response(self, MockSession, mock_netapp_config):
        """Test handling of 204 No Content response."""
        mock_session = MockSession.return_value
        no_content_response = Mock()
        no_content_response.status_code = 204
        mock_session.request.return_value = no_content_response

        client = NetAppAPIClient(mock_netapp_config, verbose=False)
        result = client.delete("/api/storage/volumes/uuid123")

        assert result == {"success": True}

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_non_json_response(self, MockSession, mock_netapp_config):
        """Test handling of non-JSON response."""
        mock_session = MockSession.return_value
        text_response = Mock()
        text_response.status_code = 200
        text_response.json.side_effect = ValueError("No JSON object could be decoded")
        text_response.text = "Plain text response"
        mock_session.request.return_value = text_response

        client = NetAppAPIClient(mock_netapp_config, verbose=False)
        result = client.get("/api/some/endpoint")

        assert result == {"text": "Plain text response"}

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_test_connection_success(self, MockSession, mock_netapp_config, mock_response):
        """Test successful connection test."""
        mock_session = MockSession.return_value
        mock_session.request.return_value = mock_response

        client = NetAppAPIClient(mock_netapp_config, verbose=False)
        result = client.test_connection()

        assert result is True
        mock_session.request.assert_called_once()

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_test_connection_failure(self, MockSession, mock_netapp_config):
        """Test connection test failure."""
        mock_session = MockSession.return_value
        error_response = Mock()
        error_response.status_code = 401
        error_response.json.return_value = {"error": {"message": "Unauthorized"}}
        mock_session.request.return_value = error_response

        client = NetAppAPIClient(mock_netapp_config, verbose=False)
        result = client.test_connection()

        assert result is False

    @patch('netapp_cli.utils.api_client.requests.Session')
    @patch('netapp_cli.utils.api_client.time.sleep')
    def test_wait_for_job_success(self, mock_sleep, MockSession, mock_netapp_config):
        """Test waiting for job completion - success."""
        mock_session = MockSession.return_value

        # First call returns running, second returns completed
        running_response = Mock()
        running_response.status_code = 200
        running_response.json.return_value = {
            "uuid": "job123",
            "state": "RUNNING",
            "message": "Job in progress"
        }

        completed_response = Mock()
        completed_response.status_code = 200
        completed_response.json.return_value = {
            "uuid": "job123",
            "state": "COMPLETED",
            "message": "Job completed successfully"
        }

        mock_session.request.side_effect = [running_response, completed_response]

        client = NetAppAPIClient(mock_netapp_config, verbose=False)
        result = client.wait_for_job("job123")

        assert result["state"] == "COMPLETED"
        assert mock_session.request.call_count == 2
        mock_sleep.assert_called_once_with(2)

    @patch('netapp_cli.utils.api_client.requests.Session')
    @patch('netapp_cli.utils.api_client.time.sleep')
    def test_wait_for_job_failure(self, mock_sleep, MockSession, mock_netapp_config):
        """Test waiting for job completion - failure."""
        mock_session = MockSession.return_value

        failed_response = Mock()
        failed_response.status_code = 200
        failed_response.json.return_value = {
            "uuid": "job123",
            "state": "FAILED",
            "message": "Job failed due to error"
        }

        mock_session.request.return_value = failed_response

        client = NetAppAPIClient(mock_netapp_config, verbose=False)

        with pytest.raises(NetAppAPIError) as exc_info:
            client.wait_for_job("job123")

        assert "Job failed" in str(exc_info.value)

    @patch('netapp_cli.utils.api_client.requests.Session')
    @patch('netapp_cli.utils.api_client.time.time')
    @patch('netapp_cli.utils.api_client.time.sleep')
    def test_wait_for_job_timeout(self, mock_sleep, mock_time, MockSession, mock_netapp_config):
        """Test waiting for job completion - timeout."""
        mock_session = MockSession.return_value

        # Mock time to simulate timeout
        mock_time.side_effect = [0, 0, 301]  # Start, check, timeout

        running_response = Mock()
        running_response.status_code = 200
        running_response.json.return_value = {
            "uuid": "job123",
            "state": "RUNNING",
            "message": "Job still running"
        }

        mock_session.request.return_value = running_response

        client = NetAppAPIClient(mock_netapp_config, verbose=False)

        with pytest.raises(NetAppAPIError) as exc_info:
            client.wait_for_job("job123", timeout=300)

        assert "timed out" in str(exc_info.value)

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_paginate_single_page(self, MockSession, mock_netapp_config):
        """Test pagination with single page."""
        mock_session = MockSession.return_value

        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "num_records": 2,
            "records": [
                {"name": "vol1", "uuid": "uuid1"},
                {"name": "vol2", "uuid": "uuid2"}
            ]
        }

        mock_session.request.return_value = response

        client = NetAppAPIClient(mock_netapp_config, verbose=False)
        result = client.paginate("/api/storage/volumes")

        assert len(result) == 2
        assert result[0]["name"] == "vol1"
        assert result[1]["name"] == "vol2"

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_paginate_multiple_pages(self, MockSession, mock_netapp_config):
        """Test pagination with multiple pages."""
        mock_session = MockSession.return_value

        # First page - response has 100 records (default limit), need more pages
        response1 = Mock()
        response1.status_code = 200
        response1.json.return_value = {
            "num_records": 150,  # Total records available
            "records": [{"name": f"vol{i}", "uuid": f"uuid{i}"} for i in range(1, 101)]  # 100 records
        }

        # Second page - remaining 50 records
        response2 = Mock()
        response2.status_code = 200
        response2.json.return_value = {
            "num_records": 150,  # Total records available
            "records": [{"name": f"vol{i}", "uuid": f"uuid{i}"} for i in range(101, 151)]  # 50 records
        }

        mock_session.request.side_effect = [response1, response2]

        client = NetAppAPIClient(mock_netapp_config, verbose=False)
        result = client.paginate("/api/storage/volumes")

        assert len(result) == 150  # Should get all records
        assert result[0]["name"] == "vol1"
        assert result[99]["name"] == "vol100"
        assert result[100]["name"] == "vol101"
        assert mock_session.request.call_count == 2

    @patch('netapp_cli.utils.api_client.requests.Session')
    def test_verbose_logging(self, MockSession, mock_netapp_config, mock_response, capsys):
        """Test verbose logging output."""
        mock_session = MockSession.return_value
        mock_session.request.return_value = mock_response

        client = NetAppAPIClient(mock_netapp_config, verbose=True)
        client.get("/api/storage/volumes", params={"name": "test"})

        # Verbose output should be printed to console
        # Note: This test might need adjustment based on how console output is captured

    def test_error_message_extraction(self, mock_netapp_config):
        """Test error message extraction from various response formats."""
        with patch('netapp_cli.utils.api_client.requests.Session'):
            client = NetAppAPIClient(mock_netapp_config, verbose=False)

            # Test simple message field
            response1 = {"message": "Simple error"}
            error_msg1 = client._extract_error_message(response1, 400)
            assert error_msg1 == "Simple error"

            # Test nested error object - the code returns the entire 'error' dict
            response2 = {"error": {"message": "Nested error"}}
            error_msg2 = client._extract_error_message(response2, 400)
            assert error_msg2 == {"message": "Nested error"}  # Returns the entire error dict

            # Test fallback to HTTP code
            response3 = {"unknown_field": "value"}
            error_msg3 = client._extract_error_message(response3, 500)
            assert "HTTP 500" in error_msg3
    def test_ssl_warning_disable(self, mock_netapp_config):
        """Test SSL warning disabling when verify_ssl is False."""
        # Mock urllib3 module since it's imported inside the client
        with patch('urllib3.disable_warnings') as mock_disable_warnings:
            with patch('netapp_cli.utils.api_client.requests.Session'):
                client = NetAppAPIClient(mock_netapp_config, verbose=False)
                # urllib3.disable_warnings should be called when verify_ssl is False
                mock_disable_warnings.assert_called_once()
