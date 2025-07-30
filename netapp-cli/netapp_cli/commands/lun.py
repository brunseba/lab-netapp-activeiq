"""LUN related commands."""

import click
from rich.console import Console

from netapp_cli.utils.api_client import NetAppAPIClient, NetAppAPIError
from netapp_cli.utils.output import OutputFormatter

console = Console()


@click.group()
def lun():
    """LUN management commands."""
    pass


@lun.command()
@click.option("--svm", help="Filter by SVM name")
@click.option("--name", help="Filter by LUN name")
@click.option("--max-records", default=100, help="Maximum number of LUNs to return")
@click.pass_context
def list(ctx, svm, name, max_records):
    """List LUNs in the storage provider."""
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

        formatter.info("Retrieving LUNs...")
        luns = client.paginate("/storage-provider/luns", params, max_records)

        if luns:
            formatter.format_output(
                luns,
                title="LUNs",
                headers=["name", "svm.name", "uuid", "size", "os_type", "state"]
            )
            formatter.info(f"Found {len(luns)} LUN(s)")
        else:
            formatter.warning("No LUNs found matching the criteria")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@lun.command()
@click.argument("lun_key")
@click.argument("new_size")
@click.option("--wait", is_flag=True, help="Wait for the operation to complete")
@click.pass_context
def expand(ctx, lun_key, new_size, wait):
    """Expand a LUN to a new size."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        # Parse size (assuming bytes, but could be enhanced to support GB, TB, etc.)
        try:
            size_bytes = int(new_size)
        except ValueError:
            formatter.error(f"Invalid size format: {new_size}. Please provide size in bytes.")
            raise click.Abort()

        expansion_data = {
            "space": {
                "size": size_bytes
            }
        }

        formatter.info(f"Expanding LUN {lun_key} to {new_size} bytes...")
        result = client.patch(f"/storage-provider/luns/{lun_key}", expansion_data)

        if wait and "key" in result:
            job_key = result["key"]
            formatter.info(f"Waiting for expansion job {job_key} to complete...")
            job_result = client.wait_for_job(job_key)
            formatter.success("LUN expansion completed successfully!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(job_result)
        else:
            formatter.success("LUN expansion initiated!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(result)

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@lun.command()
@click.argument("lun_key")
@click.pass_context
def show(ctx, lun_key):
    """Show detailed information about a specific LUN."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        formatter.info(f"Retrieving LUN details: {lun_key}")
        lun = client.get(f"/storage-provider/luns/{lun_key}")

        formatter.format_output(lun, title=f"LUN Details: {lun.get('name', 'Unknown')}")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()
