import re

class NamingConventionError(Exception):
    pass

class NamingConvention:
    ENVIRONMENTS = {"prod", "dev", "test", "stage", "qa"}
    PREFIXES = {"cluster", "vol", "snap", "lun", "share", "policy"}

    @staticmethod
    def validate(name: str, prefix: str):
        if prefix not in NamingConvention.PREFIXES:
            raise NamingConventionError(f"Invalid prefix '{prefix}'. Must be one of {NamingConvention.PREFIXES}.")

        pattern = r"^(?P<prefix>[a-z]+)-(?P<env>[a-z]+)-(?P<context>[a-z0-9-]+)-(?P<purpose>[a-z0-9-]+)-(?P<id>\d{3})$"
        match = re.match(pattern, name)
        if not match:
            raise NamingConventionError("Name does not conform to the required pattern.")

        components = match.groupdict()
        if components['prefix'] != prefix:
            raise NamingConventionError(f"Prefix mismatch. Expected '{prefix}', found '{components['prefix']}'.")
        if components['env'] not in NamingConvention.ENVIRONMENTS:
            raise NamingConventionError(f"Invalid environment '{components['env']}'. Must be one of {NamingConvention.ENVIRONMENTS}.")

        # Additional checks like length, reserved words, etc., can be added here.

        return True
