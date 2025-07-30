"""Authentication related commands."""

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm

from netapp_cli.utils.config import Config
from netapp_cli.utils.api_client import NetAppAPIClient, NetAppAPIError
from netapp_cli.utils.output import OutputFormatter

console = Console()


@click.group()
def auth():
    """Authentication management commands."""
    pass


@auth.command()
@click.option("--host", prompt="NetApp Host", help="NetApp ActiveIQ host")
@click.option("--username", prompt="Username", help="API username")
@click.option("--password", prompt="Password", hide_input=True, help="API password")
@click.option("--verify-ssl/--no-verify-ssl", default=True, help="Verify SSL certificates")
@click.option("--timeout", default=30, help="Request timeout in seconds")
@click.option("--save", is_flag=True, help="Save configuration to file")
@click.pass_context
def configure(ctx, host, username, password, verify_ssl, timeout, save):
    """Configure NetApp API authentication."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])

    try:
        # Create configuration
        config_data = {
            "netapp": {
                "host": host,
                "username": username,
                "password": password,
                "verify_ssl": verify_ssl,
                "timeout": timeout,
                "api_version": "v1"
            }
        }

        # Test connection
        formatter.info("Testing connection...")
        from netapp_cli.utils.config import NetAppConfig

        netapp_config = NetAppConfig(**config_data["netapp"])
        client = NetAppAPIClient(netapp_config, verbose=ctx.obj["verbose"])

        if client.test_connection():
            formatter.success("Connection successful!")

            if save:
                config = Config()
                config._config_data.update(config_data)
                config._netapp_config = netapp_config
                config.save_config()
                formatter.success("Configuration saved successfully!")
            else:
                formatter.info("Configuration tested but not saved. Use --save to persist.")
        else:
            formatter.error("Connection failed! Please check your credentials and host.")
            raise click.Abort()

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()
    except Exception as e:
        formatter.error(f"Configuration error: {e}")
        raise click.Abort()


@auth.command()
@click.pass_context
def test(ctx):
    """Test current authentication configuration."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    try:
        client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

        formatter.info("Testing connection...")
        if client.test_connection():
            formatter.success("Authentication successful!")

            # Get basic cluster info
            try:
                clusters = client.get("/datacenter/cluster/clusters", {"max_records": 1})
                if clusters.get("records"):
                    cluster = clusters["records"][0]
                    formatter.info(f"Connected to cluster: {cluster.get('name', 'Unknown')}")
            except:
                pass  # Don't fail if we can't get cluster info
        else:
            formatter.error("Authentication failed!")
            raise click.Abort()

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@auth.command()
@click.pass_context
def status(ctx):
    """Show current authentication status."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if config.is_configured():
        info = {
            "Host": config.netapp.host,
            "Username": config.netapp.username,
            "SSL Verification": "Enabled" if config.netapp.verify_ssl else "Disabled",
            "Timeout": f"{config.netapp.timeout}s",
            "API Version": config.netapp.api_version,
        }

        formatter.format_output(info, title="NetApp Configuration Status")

        # Test connection status
        try:
            client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])
            if client.test_connection():
                formatter.success("✓ Connection: Active")
            else:
                formatter.error("✗ Connection: Failed")
        except:
            formatter.error("✗ Connection: Error")
    else:
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")


@auth.command()
@click.pass_context
def clear(ctx):
    """Clear stored authentication configuration."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])

    if Confirm.ask("Are you sure you want to clear the stored configuration?"):
        try:
            config = Config()
            config._config_data.pop("netapp", None)
            config._netapp_config = None
            config.save_config()
            formatter.success("Configuration cleared successfully!")
        except Exception as e:
            formatter.error(f"Error clearing configuration: {e}")
            raise click.Abort()
    else:
        formatter.info("Configuration not cleared.")


@auth.command()
@click.option("--output", "-o", help="Output file path (default: ~/.netapp-cli/netapp-cli.yaml)")
@click.pass_context
def sample_config(ctx, output):
    """Create a sample configuration file."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])

    try:
        config = Config()
        config_file = config.create_sample_config(output)
        formatter.success(f"Sample configuration created: {config_file}")
        formatter.info("Edit the file with your NetApp credentials and the CLI will automatically find it.")
    except Exception as e:
        formatter.error(f"Error creating sample configuration: {e}")
        raise click.Abort()
