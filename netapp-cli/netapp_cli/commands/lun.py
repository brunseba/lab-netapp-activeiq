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


@lun.command()
@click.argument("name")
@click.option("--svm", required=True, help="SVM name")
@click.option("--volume", required=True, help="Volume name")
@click.option("--size", required=True, help="Size (e.g., 1GB, 500MB, 1TB)")
@click.option("--os-type", type=click.Choice(["linux", "windows", "vmware", "aix", "hpux", "solaris"]), default="linux", help="Operating system type")
@click.option("--comment", help="LUN comment")
@click.option("--qos-policy", help="QoS policy name")
@click.option("--wait", is_flag=True, help="Wait for the operation to complete")
@click.pass_context
def create(ctx, name, svm, volume, size, os_type, comment, qos_policy, wait):
    """Create a new LUN."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        # Parse size - convert to bytes
        from netapp_cli.commands.volume import _parse_size
        size_bytes = _parse_size(size)
        if size_bytes is None:
            formatter.error(f"Invalid size format: {size}. Use formats like '1GB', '500MB', '2TB'")
            raise click.Abort()

        # Create LUN data
        lun_data = {
            "name": name,
            "svm": {"name": svm},
            "location": {
                "volume": {"name": volume}
            },
            "space": {
                "size": size_bytes
            },
            "os_type": os_type
        }

        if comment:
            lun_data["comment"] = comment

        if qos_policy:
            lun_data["qos"] = {"policy": {"name": qos_policy}}

        formatter.info(f"Creating LUN '{name}' on SVM '{svm}' in volume '{volume}'...")
        result = client.post("/storage-provider/luns", lun_data)

        if wait and "job" in result and "key" in result["job"]:
            job_key = result["job"]["key"]
            formatter.info(f"Waiting for creation job {job_key} to complete...")
            job_result = client.wait_for_job(job_key)
            formatter.success(f"LUN '{name}' created successfully!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(job_result)
        else:
            formatter.success(f"LUN '{name}' creation initiated!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(result)

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@lun.command()
@click.argument("lun_key")
@click.option("--new-size", help="New size (e.g., 2GB, 1TB)")
@click.option("--new-comment", help="New comment")
@click.option("--qos-policy", help="QoS policy name")
@click.option("--wait", is_flag=True, help="Wait for the operation to complete")
@click.pass_context
def update(ctx, lun_key, new_size, new_comment, qos_policy, wait):
    """Update LUN properties."""
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

        if new_comment is not None:  # Allow empty string to clear comment
            update_data["comment"] = new_comment

        if qos_policy:
            update_data["qos"] = {"policy": {"name": qos_policy}}

        if not update_data:
            formatter.error("No update parameters provided. Use --help for available options.")
            raise click.Abort()

        formatter.info(f"Updating LUN '{lun_key}'...")
        result = client.patch(f"/storage-provider/luns/{lun_key}", update_data)

        if wait and "key" in result:
            job_key = result["key"]
            formatter.info(f"Waiting for update job {job_key} to complete...")
            job_result = client.wait_for_job(job_key)
            formatter.success(f"LUN '{lun_key}' updated successfully!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(job_result)
        else:
            formatter.success(f"LUN '{lun_key}' update initiated!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(result)

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@lun.command()
@click.argument("lun_key")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
@click.option("--wait", is_flag=True, help="Wait for the operation to complete")
@click.pass_context
def delete(ctx, lun_key, force, wait):
    """Delete a LUN."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    if not force:
        if not click.confirm(f"Are you sure you want to delete LUN '{lun_key}'? This action cannot be undone."):
            formatter.info("Deletion cancelled.")
            return

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        formatter.info(f"Deleting LUN '{lun_key}'...")
        result = client.delete(f"/storage-provider/luns/{lun_key}")

        if wait and "job" in result and "key" in result["job"]:
            job_key = result["job"]["key"]
            formatter.info(f"Waiting for deletion job {job_key} to complete...")
            job_result = client.wait_for_job(job_key)
            formatter.success(f"LUN '{lun_key}' deleted successfully!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(job_result)
        else:
            formatter.success(f"LUN '{lun_key}' deletion initiated!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(result)

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()
