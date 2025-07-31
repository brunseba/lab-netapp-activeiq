"""File share related commands."""

import click
from rich.console import Console

from netapp_cli.utils.api_client import NetAppAPIClient, NetAppAPIError
from netapp_cli.utils.output import OutputFormatter

console = Console()


@click.group()
def fileshare():
    """File share management commands."""
    pass


@fileshare.command()
@click.option("--svm", help="Filter by SVM name")
@click.option("--name", help="Filter by file share name")
@click.option("--max-records", default=100, help="Maximum number of file shares to return")
@click.pass_context
def list(ctx, svm, name, max_records):
    """List file shares in the storage provider."""
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

        formatter.info("Retrieving file shares...")
        fileshares = client.paginate("/storage-provider/file-shares", params, max_records)

        if fileshares:
            formatter.format_output(
                fileshares,
                title="File Shares",
                headers=["name", "svm.name", "uuid", "size", "path", "protocol"]
            )
            formatter.info(f"Found {len(fileshares)} file share(s)")
        else:
            formatter.warning("No file shares found matching the criteria")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@fileshare.command()
@click.argument("name")
@click.option("--svm", required=True, help="SVM name")
@click.option("--aggregate", required=True, help="Aggregate name")
@click.option("--size", required=True, help="Size in bytes")
@click.option("--protocol", type=click.Choice(["nfs", "cifs"]), default="nfs", help="Protocol type")
@click.option("--path", help="Export path (defaults to /name)")
@click.option("--wait", is_flag=True, help="Wait for the operation to complete")
@click.pass_context
def create(ctx, name, svm, aggregate, size, protocol, path, wait):
    """Create a new NFS file share."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        # Parse size
        try:
            size_bytes = int(size)
        except ValueError:
            formatter.error(f"Invalid size format: {size}. Please provide size in bytes.")
            raise click.Abort()

        # Create file share data
        fileshare_data = {
            "name": name,
            "svm": {"name": svm},
            "aggregate": {"name": aggregate},
            "space": {"size": size_bytes},
            "access_control": {
                "language": "c.utf_8",
                "export_path": path or f"/{name}"
            },
            "protocols": [protocol.upper()]
        }

        formatter.info(f"Creating {protocol.upper()} file share '{name}' on SVM '{svm}'...")
        result = client.post("/storage-provider/file-shares", fileshare_data)

        if wait and "job" in result and "key" in result["job"]:
            job_key = result["job"]["key"]
            formatter.info(f"Waiting for creation job {job_key} to complete...")
            job_result = client.wait_for_job(job_key)
            formatter.success(f"File share '{name}' created successfully!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(job_result)
        else:
            formatter.success(f"File share '{name}' creation initiated!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(result)

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@fileshare.command()
@click.argument("fileshare_key")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
@click.option("--wait", is_flag=True, help="Wait for the operation to complete")
@click.pass_context
def delete(ctx, fileshare_key, force, wait):
    """Delete a file share."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    if not force:
        if not click.confirm(f"Are you sure you want to delete file share '{fileshare_key}'?"):
            formatter.info("Deletion cancelled.")
            return

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        formatter.info(f"Deleting file share '{fileshare_key}'...")
        result = client.delete(f"/storage-provider/file-shares/{fileshare_key}")

        if wait and "job" in result and "key" in result["job"]:
            job_key = result["job"]["key"]
            formatter.info(f"Waiting for deletion job {job_key} to complete...")
            job_result = client.wait_for_job(job_key)
            formatter.success("File share deleted successfully!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(job_result)
        else:
            formatter.success("File share deletion initiated!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(result)

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@fileshare.command()
@click.argument("fileshare_key")
@click.pass_context
def show(ctx, fileshare_key):
    """Show detailed information about a specific file share."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        formatter.info(f"Retrieving file share details: {fileshare_key}")
        fileshare = client.get(f"/storage-provider/file-shares/{fileshare_key}")

        formatter.format_output(fileshare, title=f"File Share Details: {fileshare.get('name', 'Unknown')}")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@fileshare.command()
@click.argument("fileshare_key")
@click.option("--new-size", help="New size (e.g., 2GB, 1TB)")
@click.option("--new-export-path", help="New export path")
@click.option("--wait", is_flag=True, help="Wait for the operation to complete")
@click.pass_context
def update(ctx, fileshare_key, new_size, new_export_path, wait):
    """Update file share properties."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        # Build update data
        update_data = {}

        if new_size:
            from netapp_cli.commands.volume import _parse_size
            size_bytes = _parse_size(new_size)
            if size_bytes is None:
                formatter.error(f"Invalid size format: {new_size}. Use formats like '1GB', '500MB', '2TB'")
                raise click.Abort()
            update_data["space"] = {"size": size_bytes}

        if new_export_path is not None:
            update_data["access_control"] = {"export_path": new_export_path}

        if not update_data:
            formatter.error("No update parameters provided. Use --help for available options.")
            raise click.Abort()

        formatter.info(f"Updating file share '{fileshare_key}'...")
        result = client.patch(f"/storage-provider/file-shares/{fileshare_key}", update_data)

        if wait and "job" in result and "key" in result["job"]:
            job_key = result["job"]["key"]
            formatter.info(f"Waiting for update job {job_key} to complete...")
            job_result = client.wait_for_job(job_key)
            formatter.success(f"File share '{fileshare_key}' updated successfully!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(job_result)
        else:
            formatter.success(f"File share '{fileshare_key}' update initiated!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(result)

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()
