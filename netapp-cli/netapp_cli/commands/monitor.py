"""Monitoring and performance related commands."""

import click
from rich.console import Console

from netapp_cli.utils.api_client import NetAppAPIClient, NetAppAPIError
from netapp_cli.utils.output import OutputFormatter

console = Console()


@click.group()
def monitor():
    """Monitoring and performance commands."""
    pass


@monitor.command()
@click.option("--cluster", help="Filter by cluster name")
@click.option("--interval", default="1h", help="Time interval for metrics")
@click.option("--max-records", default=100, help="Maximum number of records to return")
@click.pass_context
def cluster_performance(ctx, cluster, interval, max_records):
    """Monitor cluster performance metrics."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        params = {"max_records": max_records, "interval": interval}
        if cluster:
            params["cluster.name"] = cluster

        formatter.info(f"Retrieving cluster performance metrics (interval: {interval})...")

        # Try to get cluster analytics data
        try:
            analytics = client.paginate("/datacenter/cluster/clusters/analytics", params, max_records)

            if analytics:
                formatter.format_output(
                    analytics,
                    title=f"Cluster Performance Metrics ({interval})",
                    headers=["cluster.name", "management_ip", "iops", "throughput", "latency"]
                )
                formatter.info(f"Found performance data for {len(analytics)} cluster(s)")
            else:
                formatter.warning("No performance data found")
        except NetAppAPIError as e:
            if e.status_code == 404:
                formatter.warning("Performance analytics endpoint not available")
                # Fallback to basic cluster info
                clusters = client.paginate("/datacenter/cluster/clusters", params, max_records)
                if clusters:
                    formatter.format_output(
                        clusters,
                        title="Clusters (Basic Info)",
                        headers=["name", "uuid", "management_ip", "version.full"]
                    )
            else:
                raise

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@monitor.command()
@click.option("--svm", help="Filter by SVM name")
@click.option("--volume", help="Filter by volume name")
@click.option("--max-records", default=100, help="Maximum number of records to return")
@click.pass_context
def volume_performance(ctx, svm, volume, max_records):
    """Monitor volume performance and usage."""
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
        if volume:
            params["name"] = volume

        formatter.info("Retrieving volume performance data...")
        volumes = client.paginate("/api/storage/volumes", params, max_records)

        if volumes:
            # Extract performance-related fields
            volume_stats = []
            for vol in volumes:
                stats = {
                    "name": vol.get("name", ""),
                    "svm.name": vol.get("svm", {}).get("name", ""),
                    "uuid": vol.get("uuid", ""),
                    "size": vol.get("space", {}).get("size", 0),
                    "used": vol.get("space", {}).get("used", 0),
                    "available": vol.get("space", {}).get("available", 0),
                    "utilization": f"{(vol.get('space', {}).get('used', 0) / max(vol.get('space', {}).get('size', 1), 1) * 100):.1f}%",
                    "state": vol.get("state", "")
                }
                volume_stats.append(stats)

            formatter.format_output(
                volume_stats,
                title="Volume Performance & Usage",
                headers=["name", "svm.name", "size", "used", "available", "utilization", "state"]
            )
            formatter.info(f"Found {len(volume_stats)} volume(s)")
        else:
            formatter.warning("No volumes found matching the criteria")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@monitor.command()
@click.option("--max-records", default=50, help="Maximum number of events to return")
@click.option("--severity", type=click.Choice(["error", "warning", "information"]), help="Filter by severity")
@click.pass_context
def events(ctx, max_records, severity):
    """Monitor system events and alerts."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        params = {"max_records": max_records, "order_by": "timestamp desc"}
        if severity:
            params["severity"] = severity

        formatter.info("Retrieving system events...")
        events = client.paginate("/management-server/events", params, max_records)

        if events:
            formatter.format_output(
                events,
                title="System Events",
                headers=["name", "severity", "timestamp", "source.name", "message"]
            )
            formatter.info(f"Found {len(events)} event(s)")
        else:
            formatter.warning("No events found matching the criteria")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@monitor.command()
@click.option("--max-records", default=50, help="Maximum number of jobs to return")
@click.option("--state", type=click.Choice(["running", "completed", "failed"]), help="Filter by job state")
@click.pass_context
def jobs(ctx, max_records, state):
    """Monitor background jobs."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        params = {"max_records": max_records, "order_by": "start_time desc"}
        if state:
            params["state"] = state.upper()

        formatter.info("Retrieving background jobs...")
        jobs = client.paginate("/management-server/jobs", params, max_records)

        if jobs:
            formatter.format_output(
                jobs,
                title="Background Jobs",
                headers=["uuid", "description", "state", "start_time", "end_time", "message"]
            )
            formatter.info(f"Found {len(jobs)} job(s)")
        else:
            formatter.warning("No jobs found matching the criteria")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()


@monitor.command()
@click.pass_context
def health(ctx):
    """Get overall system health status."""
    formatter = OutputFormatter(ctx.obj["output_format"], ctx.obj["verbose"])
    config = ctx.obj["config"]

    if not config.is_configured():
        formatter.error("No NetApp configuration found. Run 'netapp auth configure' first.")
        raise click.Abort()

    client = NetAppAPIClient(config.netapp, verbose=ctx.obj["verbose"])

    try:
        formatter.info("Retrieving system health status...")

        # Get cluster status
        clusters = client.get("/datacenter/cluster/clusters", {"max_records": 10})
        cluster_count = clusters.get("num_records", 0)

        # Get SVM status
        svms = client.get("/storage-provider/svms", {"max_records": 10})
        svm_count = svms.get("num_records", 0)

        # Get volume status
        volumes = client.get("/api/storage/volumes", {"max_records": 10})
        volume_count = volumes.get("num_records", 0)

        # Get recent events (errors and warnings)
        events = client.get("/management-server/events", {
            "max_records": 5,
            "severity": "error,warning",
            "order_by": "timestamp desc"
        })
        recent_issues = events.get("num_records", 0)

        health_summary = {
            "clusters": cluster_count,
            "svms": svm_count,
            "volumes": volume_count,
            "recent_issues": recent_issues,
            "overall_status": "healthy" if recent_issues == 0 else "issues_detected"
        }

        formatter.format_output(health_summary, title="System Health Summary")

        if recent_issues > 0:
            formatter.warning(f"Found {recent_issues} recent issue(s). Use 'netapp monitor events' for details.")
        else:
            formatter.success("No recent issues detected.")

    except NetAppAPIError as e:
        formatter.error(f"API Error: {e}")
        raise click.Abort()
