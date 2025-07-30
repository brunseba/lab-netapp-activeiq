"""Volume related commands."""

import click
from rich.console import Console

from netapp_cli.utils.api_client import NetAppAPIClient, NetAppAPIError
from netapp_cli.utils.output import OutputFormatter

console = Console()

@click.group()
def volume():
    """Volume management commands."""
    pass


@volume.command()
@click.option("--svm", required=True, help="SVM name")
@click.pass_context
def list(ctx, svm):
    """List volumes in an SVM."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    client = NetAppAPIClient(ctx.obj["config"].netapp, verbose=ctx.obj["verbose"])

    try:
        formatter.info(f"Listing volumes for SVM: {svm}")
        response = client.get("/api/storage/volumes", {"svm.name": svm})
        volumes = response.get("records", [])

        if volumes:
            formatter.format_output(volumes, headers=["name", "uuid", "size.total", "state"])
        else:
            formatter.warning(f"No volumes found for SVM: {svm}")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@volume.command()
@click.option("--svm", help="SVM name (optional)")
@click.option("--name", help="Volume name filter")
@click.option("--max-records", default=100, help="Maximum number of records to return")
@click.pass_context
def list_volumes(ctx, svm, name, max_records):
    """List volumes with optional filtering."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        params = {"max_records": max_records}
        if svm:
            params["svm.name"] = svm
        if name:
            params["name"] = name

        formatter.info("Retrieving volumes...")
        volumes = client.paginate("/api/storage/volumes", params, max_records)

        if volumes:
            formatter.format_output(
                volumes,
                title="Volumes",
                headers=["name", "svm.name", "uuid", "size", "state", "style"]
            )
            formatter.info(f"Found {len(volumes)} volume(s)")
        else:
            formatter.warning("No volumes found matching the criteria")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@volume.command()
@click.argument("volume_name")
@click.option("--svm", help="SVM name")
@click.option("--skip-naming-validation", is_flag=True, help="Skip naming convention validation")
@click.pass_context
def show(ctx, volume_name, svm, skip_naming_validation):
    """Show detailed information about a specific volume."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    # Validate naming convention unless explicitly skipped
    if not skip_naming_validation and config.get("naming_convention", {}).get("enabled", True):
        from netapp_cli.utils.naming import NamingConvention, NamingConventionError
        try:
            NamingConvention.validate(volume_name, "vol")
            formatter.info(f"✓ Volume name '{volume_name}' follows naming convention")
        except NamingConventionError as e:
            formatter.warning(f"Naming convention violation: {e}")
            if not click.confirm("Continue anyway?"):
                raise click.Abort()

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        # First find the volume
        params = {"name": volume_name}
        if svm:
            params["svm.name"] = svm

        formatter.info(f"Looking up volume: {volume_name}")
        response = client.get("/api/storage/volumes", params)
        volumes = response.get("records", [])

        if not volumes:
            formatter.error(f"Volume '{volume_name}' not found")
            raise click.Abort()

        volume = volumes[0]
        volume_uuid = volume["uuid"]

        # Get detailed volume information
        detailed_volume = client.get(f"/api/storage/volumes/{volume_uuid}")

        formatter.format_output(detailed_volume, title=f"Volume Details: {volume_name}")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()
