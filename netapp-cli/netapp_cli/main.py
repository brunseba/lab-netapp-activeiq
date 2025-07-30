#!/usr/bin/env python3
"""
NetApp ActiveIQ CLI Tool
Main entry point for the NetApp API CLI commands.
"""

import click
from rich.console import Console
from rich.table import Table

from netapp_cli.commands import auth, cluster, volume, snapshot, lun, fileshare, monitor
from netapp_cli.utils.config import Config

console = Console()


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--output", "-o", type=click.Choice(["table", "json", "yaml"]), default="table", help="Output format")
@click.pass_context
def cli(ctx, config, verbose, output):
    """NetApp ActiveIQ API CLI Tool.

    A comprehensive command-line interface to interact with ActiveIQ Server.
    Supports management of NetApp storage systems through the ActiveIQ API.
    Includes features like storage provisioning, monitoring, snapshot management, and more.
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = Config(config_file=config) if config else Config()
    ctx.obj["verbose"] = verbose
    ctx.obj["output_format"] = output

    if verbose:
        console.print("[dim]NetApp CLI initialized with verbose output[/dim]")


@cli.command()
def version():
    """Show version information."""
    from netapp_cli import __version__

    table = Table(title="NetApp CLI Version")
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="green")

    table.add_row("NetApp CLI", __version__)
    table.add_row("Python", click.__version__)

    console.print(table)


# Register command groups
cli.add_command(auth.auth)
cli.add_command(cluster.cluster)
cli.add_command(volume.volume)
cli.add_command(snapshot.snapshot)
cli.add_command(lun.lun)
cli.add_command(fileshare.fileshare)
cli.add_command(monitor.monitor)


if __name__ == "__main__":
    cli()
