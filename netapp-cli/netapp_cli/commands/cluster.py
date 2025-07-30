"""Cluster related commands."""

import click
from rich.console import Console

from netapp_cli.utils.api_client import NetAppAPIClient, NetAppAPIError
from netapp_cli.utils.output import OutputFormatter

console = Console()


@click.group()
def cluster():
    """Cluster management commands."""
    pass


@cluster.command()
@click.option("--name", help="Filter by cluster name")
@click.option("--uuid", help="Filter by cluster UUID")
@click.option("--max-records", default=100, help="Maximum number of clusters to return")
@click.pass_context
def list(ctx, name, uuid, max_records):
    """List clusters in the datacenter."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        params = {"max_records": max_records}
        if name:
            params["name"] = name
        if uuid:
            params["uuid"] = uuid

        formatter.info("Retrieving clusters...")
        clusters = client.paginate("/datacenter/cluster/clusters", params, max_records)

        if clusters:
            formatter.format_output(
                clusters,
                title="Clusters",
                headers=["name", "uuid", "management_ip", "location", "version.full", "contact"]
            )
            formatter.info(f"Found {len(clusters)} cluster(s)")
        else:
            formatter.warning("No clusters found matching the criteria")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@cluster.command()
@click.argument("cluster_key")
@click.pass_context
def show(ctx, cluster_key):
    """Show detailed information about a specific cluster."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        formatter.info(f"Retrieving cluster details: {cluster_key}")
        cluster = client.get(f"/datacenter/cluster/clusters/{cluster_key}")

        formatter.format_output(cluster, title=f"Cluster Details: {cluster.get('name', 'Unknown')}")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@cluster.command()
@click.option("--cluster", help="Filter by cluster name or UUID")
@click.option("--max-records", default=100, help="Maximum number of records to return")
@click.pass_context
def performance(ctx, cluster, max_records):
    """Show cluster performance analytics."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        params = {"max_records": max_records}
        if cluster:
            params["cluster.name"] = cluster

        formatter.info("Retrieving cluster performance data...")
        analytics = client.paginate("/datacenter/cluster/clusters/analytics", params, max_records)

        if analytics:
            formatter.format_output(
                analytics,
                title="Cluster Performance Analytics",
                headers=["cluster.name", "management_ip", "iops", "throughput", "latency"]
            )
            formatter.info(f"Found performance data for {len(analytics)} cluster(s)")
        else:
            formatter.warning("No performance data found")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@cluster.command()
@click.option("--max-records", default=100, help="Maximum number of SVMs to return")
@click.pass_context
def svms(ctx, max_records):
    """List SVMs across all clusters."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        formatter.info("Retrieving SVMs...")
        svms = client.paginate("/storage-provider/svms", {"max_records": max_records}, max_records)

        if svms:
            formatter.format_output(
                svms,
                title="Storage Virtual Machines (SVMs)",
                headers=["name", "uuid", "cluster.name", "state", "subtype"]
            )
            formatter.info(f"Found {len(svms)} SVM(s)")
        else:
            formatter.warning("No SVMs found")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@cluster.command()
@click.option("--cluster", help="Filter by cluster name")
@click.option("--max-records", default=100, help="Maximum number of aggregates to return")
@click.pass_context
def aggregates(ctx, cluster, max_records):
    """List aggregates across clusters."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        params = {"max_records": max_records}
        if cluster:
            params["cluster.name"] = cluster

        formatter.info("Retrieving aggregates...")
        aggregates = client.paginate("/datacenter/storage/aggregates", params, max_records)

        if aggregates:
            formatter.format_output(
                aggregates,
                title="Storage Aggregates",
                headers=["name", "uuid", "cluster.name", "state", "space.size", "space.used"]
            )
            formatter.info(f"Found {len(aggregates)} aggregate(s)")
        else:
            formatter.warning("No aggregates found")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()
