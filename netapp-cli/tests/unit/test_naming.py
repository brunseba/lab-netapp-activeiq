"""Tests for naming convention utilities."""

import pytest
from netapp_cli.utils.naming import NamingConvention, NamingConventionError


class TestNamingConvention:
    """Tests for naming convention validation."""

    def test_valid_volume_names(self):
        """Test valid volume names."""
        valid_names = [
            "vol-prod-web-data-001",
            "vol-dev-api-logs-123",
            "vol-test-db-backup-999",
            "vol-stage-app-cache-042"
        ]

        for name in valid_names:
            assert NamingConvention.validate(name, "vol") is True

    def test_valid_different_prefixes(self):
        """Test valid names with different prefixes."""
        test_cases = [
            ("cluster-prod-web-primary-001", "cluster"),
            ("snap-dev-daily-backup-001", "snap"),
            ("lun-prod-db-data-001", "lun"),
            ("share-test-user-home-001", "share"),
            ("policy-prod-backup-weekly-001", "policy")
        ]

        for name, prefix in test_cases:
            assert NamingConvention.validate(name, prefix) is True

    def test_invalid_prefix_validation(self):
        """Test validation with invalid prefixes."""
        with pytest.raises(NamingConventionError, match="Invalid prefix"):
            NamingConvention.validate("vol-prod-web-data-001", "invalid")

    def test_invalid_name_format(self):
        """Test invalid name formats."""
        invalid_names = [
            "volume-prod-web-data-001",  # wrong prefix
            "vol_prod_web_data_001",     # underscores instead of hyphens
            "vol-prod-web-data",         # missing ID number
            "vol-prod-web-data-abc",     # non-numeric ID
            "vol-prod",                  # too few segments
            "vol-prod-web-data-001-extra",  # too many segments
            "VOL-PROD-WEB-DATA-001",     # uppercase
            "vol--prod-web-data-001",    # double hyphen
            "vol-prod-web-data-1",       # ID not 3 digits
            "vol-prod-web-data-0001"     # ID more than 3 digits
        ]

        for name in invalid_names:
            with pytest.raises(NamingConventionError):
                NamingConvention.validate(name, "vol")

    def test_invalid_environment(self):
        """Test invalid environment names."""
        invalid_env_names = [
            "vol-production-web-data-001",  # 'production' not in allowed envs
            "vol-develop-web-data-001",     # 'develop' not in allowed envs
            "vol-sit-web-data-001",         # 'sit' not in allowed envs
            "vol-uat-web-data-001"          # 'uat' not in allowed envs
        ]

        for name in invalid_env_names:
            with pytest.raises(NamingConventionError, match="Invalid environment"):
                NamingConvention.validate(name, "vol")

    def test_valid_environments(self):
        """Test all valid environments."""
        valid_environments = ["prod", "dev", "test", "stage", "qa"]

        for env in valid_environments:
            name = f"vol-{env}-web-data-001"
            assert NamingConvention.validate(name, "vol") is True

    def test_prefix_mismatch(self):
        """Test prefix mismatch detection."""
        with pytest.raises(NamingConventionError, match="Prefix mismatch"):
            NamingConvention.validate("lun-prod-web-data-001", "vol")

    def test_environments_set(self):
        """Test that environments is a proper set."""
        assert isinstance(NamingConvention.ENVIRONMENTS, set)
        expected_envs = {"prod", "dev", "test", "stage", "qa"}
        assert NamingConvention.ENVIRONMENTS == expected_envs

    def test_prefixes_set(self):
        """Test that prefixes is a proper set."""
        assert isinstance(NamingConvention.PREFIXES, set)
        expected_prefixes = {"cluster", "vol", "snap", "lun", "share", "policy"}
        assert NamingConvention.PREFIXES == expected_prefixes

    def test_complex_valid_names(self):
        """Test complex but valid names."""
        complex_names = [
            "vol-prod-web-server-logs-001",
            "lun-dev-database-primary-999",
            "snap-test-backup-incremental-123",
            "share-stage-user-temp-files-456",
            "policy-qa-retention-long-term-789"
        ]

        prefixes = ["vol", "lun", "snap", "share", "policy"]

        for name, prefix in zip(complex_names, prefixes):
            assert NamingConvention.validate(name, prefix) is True

    def test_edge_cases(self):
        """Test edge cases for naming validation."""
        # Minimum valid name
        assert NamingConvention.validate("vol-dev-a-b-000", "vol") is True

        # Names with numbers in context/purpose
        assert NamingConvention.validate("vol-prod-web2-data3-001", "vol") is True

        # Names with hyphens in context/purpose
        assert NamingConvention.validate("vol-prod-web-app-server-data-001", "vol") is True

    def test_naming_convention_error(self):
        """Test NamingConventionError exception."""
        error = NamingConventionError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_regex_pattern_components(self):
        """Test that regex pattern captures all components correctly."""
        name = "vol-prod-web-data-001"

        import re
        pattern = r"^(?P<prefix>[a-z]+)-(?P<env>[a-z]+)-(?P<context>[a-z0-9-]+)-(?P<purpose>[a-z0-9-]+)-(?P<id>\d{3})$"
        match = re.match(pattern, name)

        assert match is not None
        components = match.groupdict()
        assert components['prefix'] == 'vol'
        assert components['env'] == 'prod'
        assert components['context'] == 'web'
        assert components['purpose'] == 'data'
        assert components['id'] == '001'

    @pytest.mark.parametrize("name,prefix,should_pass", [
        ("vol-prod-web-data-001", "vol", True),
        ("lun-dev-db-logs-123", "lun", True),
        ("vol-invalid-web-data-001", "vol", False),  # invalid env
        ("invalid-prod-web-data-001", "vol", False), # prefix mismatch
        ("vol-prod-web-data-1", "vol", False),       # invalid ID format
        ("vol-prod-web-data-abc", "vol", False),     # non-numeric ID
    ])
    def test_parametrized_validation(self, name, prefix, should_pass):
        """Parametrized test for various naming scenarios."""
        if should_pass:
            assert NamingConvention.validate(name, prefix) is True
        else:
            with pytest.raises(NamingConventionError):
                NamingConvention.validate(name, prefix)
