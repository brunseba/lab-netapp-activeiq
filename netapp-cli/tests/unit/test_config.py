"""Tests for configuration management."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from netapp_cli.utils.config import Config, NetAppConfig


class TestNetAppConfig:
    """Tests for NetAppConfig model."""

    def test_valid_config(self):
        """Test valid configuration creation."""
        config = NetAppConfig(
            host="test-cluster.example.com",
            username="admin",
            password="secret123"
        )
        assert config.host == "test-cluster.example.com"
        assert config.username == "admin"
        assert config.password == "secret123"
        assert config.verify_ssl is True  # default
        assert config.timeout == 30  # default
        assert config.api_version == "v1"  # default

    def test_config_with_custom_values(self):
        """Test configuration with custom values."""
        config = NetAppConfig(
            host="custom-host.com",
            username="user",
            password="pass",
            verify_ssl=False,
            timeout=60,
            api_version="v2"
        )
        assert config.verify_ssl is False
        assert config.timeout == 60
        assert config.api_version == "v2"

    def test_config_validation(self):
        """Test configuration validation."""
        # Missing required fields should raise validation error
        with pytest.raises(ValueError):
            NetAppConfig()

        with pytest.raises(ValueError):
            NetAppConfig(host="test.com")  # missing username and password


class TestConfig:
    """Tests for Config class."""

    def test_config_from_file(self, temp_config_file):
        """Test loading configuration from file."""
        config = Config(config_file=temp_config_file)

        assert config.is_configured()
        assert config.netapp.host == "test-cluster.example.com"
        assert config.netapp.username == "admin"
        assert config.netapp.password == "secret123"
        assert config.netapp.verify_ssl is False
        assert config.netapp.timeout == 30

    def test_config_without_file(self):
        """Test configuration without file."""
        with patch.object(Config, '_find_config_file', return_value=None):
            config = Config()
            assert not config.is_configured()
            assert config.netapp is None

    def test_find_config_file(self, temp_config_file):
        """Test finding configuration file."""
        # Test with existing file
        config = Config(config_file=temp_config_file)
        assert config.config_file == temp_config_file

        # Test with non-existent file
        with patch.object(Path, 'exists', return_value=False):
            config = Config()
            assert config.config_file is None

    @patch.dict(os.environ, {
        'NETAPP_HOST': 'env-host.com',
        'NETAPP_USERNAME': 'env-user',
        'NETAPP_PASSWORD': 'env-pass',
        'NETAPP_VERIFY_SSL': 'false',
        'NETAPP_TIMEOUT': '45'
    })
    def test_environment_override(self):
        """Test environment variable override."""
        with patch.object(Config, '_find_config_file', return_value=None):
            config = Config()
            assert config.is_configured()
            assert config.netapp.host == "env-host.com"
            assert config.netapp.username == "env-user"
            assert config.netapp.password == "env-pass"
            assert config.netapp.verify_ssl is False
            assert config.netapp.timeout == 45

    def test_invalid_yaml_config(self):
        """Test handling invalid YAML configuration."""
        invalid_yaml_content = """
        netapp:
          host: test.com
          username: admin
          # Invalid YAML - missing closing bracket
          password: [unclosed
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml_content)
            f.flush()

            # Should handle YAML parsing errors gracefully
            with pytest.raises(Exception):  # Could be YAML or validation error
                Config(config_file=f.name)

        os.unlink(f.name)

    def test_save_config(self, temp_config_file):
        """Test saving configuration."""
        config = Config(config_file=temp_config_file)

        # Modify configuration
        config._config_data['test_key'] = 'test_value'

        # Save to new file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            new_config_file = f.name

        config.save_config(new_config_file)

        # Load the saved configuration
        new_config = Config(config_file=new_config_file)
        assert new_config.get('test_key') == 'test_value'

        # Cleanup
        os.unlink(new_config_file)

    def test_create_sample_config(self):
        """Test creating sample configuration."""
        config = Config()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            sample_file = f.name

        created_file = config.create_sample_config(sample_file)
        assert created_file == sample_file
        assert Path(sample_file).exists()

        # Verify sample config structure
        sample_config = Config(config_file=sample_file)
        assert 'netapp' in sample_config._config_data
        assert 'output' in sample_config._config_data
        assert 'logging' in sample_config._config_data

        # Cleanup
        os.unlink(sample_file)

    def test_get_method(self, temp_config_file):
        """Test get method for configuration values."""
        config = Config(config_file=temp_config_file)

        # Test existing key
        assert config.get('output') is not None

        # Test non-existing key with default
        assert config.get('non_existing_key', 'default') == 'default'

        # Test non-existing key without default
        assert config.get('non_existing_key') is None

    def test_config_file_search_paths(self):
        """Test configuration file search in multiple locations."""
        config = Config()

        # Should search in predefined locations
        expected_paths = [
            "~/.netapp-cli/netapp-cli.yaml",
            "~/.netapp-cli/netapp-cli.yml",
            "netapp-cli.yaml",
            "netapp-cli.yml",
            "~/.netapp-cli.yaml",
            "~/.netapp-cli.yml",
            "~/.config/netapp-cli/config.yaml",
            "~/.config/netapp-cli/config.yml"
        ]

        # Mock Path.exists to return False for all paths
        with patch.object(Path, 'exists', return_value=False):
            found_file = config._find_config_file()
            assert found_file is None

    def test_config_directory_creation(self):
        """Test configuration directory creation during save."""
        config = Config()

        # Create a temporary directory path that doesn't exist
        temp_dir = Path(tempfile.gettempdir()) / "test_netapp_cli_config"
        config_file = temp_dir / "test_config.yaml"

        # Ensure directory doesn't exist
        if temp_dir.exists():
            temp_dir.rmdir()

        # Save config should create directory
        config.save_config(str(config_file))

        assert temp_dir.exists()
        assert config_file.exists()

        # Cleanup
        config_file.unlink()
        temp_dir.rmdir()

    @patch.dict(os.environ, {
        'NETAPP_HOST': 'test.com',
        'NETAPP_USERNAME': 'user',
        'NETAPP_PASSWORD': 'pass',
        'NETAPP_VERIFY_SSL': 'invalid_boolean'  # Invalid boolean value
    })
    def test_invalid_environment_values(self):
        """Test handling of invalid environment variable values."""
        with patch.object(Config, '_find_config_file', return_value=None):
            config = Config()
            # Should handle invalid boolean value gracefully
            # The config should still be created, but verify_ssl should be False
            # because 'invalid_boolean'.lower() != 'true'
            assert config.is_configured()
            assert config.netapp.verify_ssl is False
