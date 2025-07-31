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


@volume.command()
@click.argument("name")
@click.option("--svm", required=True, help="SVM name")
@click.option("--aggregate", required=True, help="Aggregate name")
@click.option("--size", required=True, help="Size (e.g., 1GB, 500MB, 1TB)")
@click.option("--type", "volume_type", type=click.Choice(["rw", "dp", "ls"]), default="rw", help="Volume type")
@click.option("--style", type=click.Choice(["flexvol", "flexgroup"]), default="flexvol", help="Volume style")
@click.option("--junction-path", help="Junction path for NAS volumes")
@click.option("--language", default="c.utf_8", help="Language setting")
@click.option("--comment", help="Volume comment")
@click.option("--wait", is_flag=True, help="Wait for the operation to complete")
@click.option("--skip-naming-validation", is_flag=True, help="Skip naming convention validation")
@click.pass_context
def create(ctx, name, svm, aggregate, size, volume_type, style, junction_path, language, comment, wait, skip_naming_validation):
    """Create a new volume."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    # Validate naming convention unless explicitly skipped
    if not skip_naming_validation and config.get("naming_convention", {}).get("enabled", True):
        from netapp_cli.utils.naming import NamingConvention, NamingConventionError
        try:
            NamingConvention.validate(name, "vol")
            formatter.info(f"✓ Volume name '{name}' follows naming convention")
        except NamingConventionError as e:
            formatter.warning(f"Naming convention violation: {e}")
            if not click.confirm("Continue anyway?"):
                raise click.Abort()

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        # Parse size - convert to bytes
        size_bytes = _parse_size(size)
        if size_bytes is None:
            formatter.error(f"Invalid size format: {size}. Use formats like '1GB', '500MB', '2TB'")
            raise click.Abort()

        # Create volume data
        volume_data = {
            "name": name,
            "svm": {"name": svm},
            "aggregates": [{"name": aggregate}],
            "size": size_bytes,
            "type": volume_type,
            "style": style,
            "language": language
        }

        if junction_path:
            volume_data["nas"] = {"path": junction_path}

        if comment:
            volume_data["comment"] = comment

        formatter.info(f"Creating volume '{name}' on SVM '{svm}' in aggregate '{aggregate}'...")
        result = client.post("/api/storage/volumes", volume_data)

        if wait and "job" in result and "uuid" in result["job"]:
            job_uuid = result["job"]["uuid"]
            formatter.info(f"Waiting for creation job {job_uuid} to complete...")
            job_result = client.wait_for_job(job_uuid)
            formatter.success(f"Volume '{name}' created successfully!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(job_result)
        else:
            formatter.success(f"Volume '{name}' creation initiated!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(result)

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@volume.command()
@click.argument("volume_name")
@click.option("--svm", help="SVM name")
@click.option("--new-size", help="New size (e.g., 2GB, 1TB)")
@click.option("--new-comment", help="New comment")
@click.option("--new-junction-path", help="New junction path")
@click.option("--snapshot-policy", help="Snapshot policy name")
@click.option("--wait", is_flag=True, help="Wait for the operation to complete")
@click.pass_context
def update(ctx, volume_name, svm, new_size, new_comment, new_junction_path, snapshot_policy, wait):
    """Update volume properties."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

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

        volume_uuid = volumes[0]["uuid"]

        # Build update data
        update_data = {}

        if new_size:
            size_bytes = _parse_size(new_size)
            if size_bytes is None:
                formatter.error(f"Invalid size format: {new_size}. Use formats like '1GB', '500MB', '2TB'")
                raise click.Abort()
            update_data["size"] = size_bytes

        if new_comment is not None:  # Allow empty string to clear comment
            update_data["comment"] = new_comment

        if new_junction_path is not None:
            update_data["nas"] = {"path": new_junction_path}

        if snapshot_policy:
            update_data["snapshot_policy"] = {"name": snapshot_policy}

        if not update_data:
            formatter.error("No update parameters provided. Use --help for available options.")
            raise click.Abort()

        formatter.info(f"Updating volume '{volume_name}'...")
        result = client.patch(f"/api/storage/volumes/{volume_uuid}", update_data)

        if wait and "job" in result and "uuid" in result["job"]:
            job_uuid = result["job"]["uuid"]
            formatter.info(f"Waiting for update job {job_uuid} to complete...")
            job_result = client.wait_for_job(job_uuid)
            formatter.success(f"Volume '{volume_name}' updated successfully!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(job_result)
        else:
            formatter.success(f"Volume '{volume_name}' update initiated!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(result)

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@volume.command()
@click.argument("volume_name")
@click.option("--svm", help="SVM name")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
@click.option("--wait", is_flag=True, help="Wait for the operation to complete")
@click.pass_context
def delete(ctx, volume_name, svm, force, wait):
    """Delete a volume."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    if not force:
        if not click.confirm(f"Are you sure you want to delete volume '{volume_name}'? This action cannot be undone."):
            formatter.info("Deletion cancelled.")
            return

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

        volume_uuid = volumes[0]["uuid"]

        formatter.info(f"Deleting volume '{volume_name}'...")
        result = client.delete(f"/api/storage/volumes/{volume_uuid}")

        if wait and "job" in result and "uuid" in result["job"]:
            job_uuid = result["job"]["uuid"]
            formatter.info(f"Waiting for deletion job {job_uuid} to complete...")
            job_result = client.wait_for_job(job_uuid)
            formatter.success(f"Volume '{volume_name}' deleted successfully!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(job_result)
        else:
            formatter.success(f"Volume '{volume_name}' deletion initiated!")
            if ctx.obj["output_format"] != "table":
                formatter.format_output(result)

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


def _parse_size(size_str):
    """Parse size string to bytes."""
    import re

    # Handle pure number (assume bytes)
    if size_str.isdigit():
        return int(size_str)

    # Parse size with unit
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B?)$', size_str.upper())
    if not match:
        return None

    size_value = float(match.group(1))
    unit = match.group(2)

    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4,
        'K': 1024,
        'M': 1024**2,
        'G': 1024**3,
        'T': 1024**4
    }

    return int(size_value * multipliers.get(unit, 1))
