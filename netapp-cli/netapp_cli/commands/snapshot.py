"""Snapshot related commands."""

import click
from rich.console import Console

from netapp_cli.utils.api_client import NetAppAPIClient, NetAppAPIError
from netapp_cli.utils.output import OutputFormatter

console = Console()


@click.group()
def snapshot():
    """Snapshot management commands."""
    pass


@snapshot.command()
@click.argument("volume_name")
@click.option("--svm", help="SVM name")
@click.option("--max-records", default=100, help="Maximum number of snapshots to return")
@click.option("--order-by", default="create_time desc", help="Sort order")
@click.pass_context
def list(ctx, volume_name, svm, max_records, order_by):
    """List snapshots for a volume."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        # First find the volume UUID
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
        formatter.progress_update(f"Found volume UUID: {volume_uuid}")

        # Get snapshots for the volume
        formatter.info(f"Retrieving snapshots for volume: {volume_name}")
        snapshots_params = {
            "max_records": max_records,
            "order_by": order_by
        }

        snapshots = client.paginate(
            f"/api/storage/volumes/{volume_uuid}/snapshots",
            snapshots_params,
            max_records
        )

        if snapshots:
            formatter.format_output(
                snapshots,
                title=f"Snapshots for Volume: {volume_name}",
                headers=["name", "uuid", "create_time", "size", "state"]
            )
            formatter.info(f"Found {len(snapshots)} snapshot(s)")
        else:
            formatter.warning(f"No snapshots found for volume: {volume_name}")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@snapshot.command()
@click.argument("volume_name")
@click.argument("snapshot_name")
@click.option("--svm", help="SVM name")
@click.option("--comment", help="Snapshot comment")
@click.pass_context
def create(ctx, volume_name, snapshot_name, svm, comment):
    """Create a snapshot for a volume."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        # First find the volume UUID
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

        # Create snapshot
        snapshot_data = {
            "name": snapshot_name
        }
        if comment:
            snapshot_data["comment"] = comment

        formatter.info(f"Creating snapshot '{snapshot_name}' for volume '{volume_name}'")
        result = client.post(f"/api/storage/volumes/{volume_uuid}/snapshots", snapshot_data)

        formatter.success(f"Snapshot '{snapshot_name}' created successfully!")
        if ctx.obj["output_format"] != "table":
            formatter.format_output(result)

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@snapshot.command()
@click.argument("volume_name")
@click.argument("snapshot_name")
@click.option("--svm", help="SVM name")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
@click.pass_context
def delete(ctx, volume_name, snapshot_name, svm, force):
    """Delete a snapshot from a volume."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    if not force:
        if not click.confirm(f"Are you sure you want to delete snapshot '{snapshot_name}' from volume '{volume_name}'?"):
            formatter.info("Deletion cancelled.")
            return

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        # First find the volume UUID
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

        # Find the snapshot UUID
        formatter.info(f"Looking up snapshot: {snapshot_name}")
        snapshot_response = client.get(
            f"/api/storage/volumes/{volume_uuid}/snapshots",
            {"name": snapshot_name}
        )
        snapshots = snapshot_response.get("records", [])

        if not snapshots:
            formatter.error(f"Snapshot '{snapshot_name}' not found")
            raise click.Abort()

        snapshot_uuid = snapshots[0]["uuid"]

        # Delete snapshot
        formatter.info(f"Deleting snapshot '{snapshot_name}' from volume '{volume_name}'")
        client.delete(f"/api/storage/volumes/{volume_uuid}/snapshots/{snapshot_uuid}")

        formatter.success(f"Snapshot '{snapshot_name}' deleted successfully!")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@snapshot.command()
@click.option("--max-records", default=100, help="Maximum number of policies to return")
@click.pass_context
def list_policies(ctx, max_records):
    """List snapshot policies."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        formatter.info("Retrieving snapshot policies...")
        policies = client.paginate("/api/storage/snapshot-policies", {"max_records": max_records}, max_records)

        if policies:
            formatter.format_output(
                policies,
                title="Snapshot Policies",
                headers=["name", "uuid", "svm.name", "comment", "enabled"]
            )
            formatter.info(f"Found {len(policies)} policy/policies")
        else:
            formatter.warning("No snapshot policies found")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@snapshot.command()
@click.argument("policy_name")
@click.option("--svm", required=True, help="SVM name")
@click.option("--comment", help="Policy comment")
@click.option("--schedule", multiple=True, help="Schedule in format 'name:count' (e.g., 'daily:7')")
@click.pass_context
def create_policy(ctx, policy_name, svm, comment, schedule):
    """Create a new snapshot policy.

    Example:
    netapp snapshot create-policy my_policy --svm svm1 --schedule daily:7 --schedule weekly:4
    """
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        # Parse schedules
        schedules = []
        for sched in schedule:
            if ":" not in sched:
                formatter.error(f"Invalid schedule format: {sched}. Use 'name:count' format.")
                raise click.Abort()

            name, count = sched.split(":", 1)
            schedules.append({
                "schedule": {"name": name.strip()},
                "count": int(count.strip())
            })

        if not schedules:
            formatter.error("At least one schedule must be specified")
            raise click.Abort()

        # Create policy data
        policy_data = {
            "name": policy_name,
            "svm": {"name": svm},
            "schedules": schedules
        }

        if comment:
            policy_data["comment"] = comment

        formatter.info(f"Creating snapshot policy '{policy_name}' for SVM '{svm}'")
        result = client.post("/api/storage/snapshot-policies", policy_data)

        formatter.success(f"Snapshot policy '{policy_name}' created successfully!")
        if ctx.obj["output_format"] != "table":
            formatter.format_output(result)

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()
    except ValueError as e:
        formatter.error(f"Invalid schedule count: {e}")
        raise click.Abort()
