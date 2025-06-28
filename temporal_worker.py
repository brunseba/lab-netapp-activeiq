"""
Temporal Worker for NetApp ActiveIQ API Workflows

This module implements the Temporal worker that executes workflows and activities
for NetApp infrastructure management.
"""

import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

from temporal_workflows import (
    # Import all workflows
    SVMCreationWorkflow,
    NFSShareProvisioningWorkflow,
    PerformanceMonitoringWorkflow,
    EventProcessingWorkflow,
    ComprehensiveStorageProvisioningWorkflow,
    
    # Import all activities
    validate_cluster_health,
    get_available_aggregates,
    create_svm,
    monitor_job_completion,
    create_nfs_share,
    get_performance_metrics,
    check_alert_thresholds,
    send_notification,
    get_system_events,
    acknowledge_event,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    Main function to start the Temporal worker.
    """
    # Connect to Temporal Server
    client = await Client.connect("localhost:7233")
    
    # Create and start worker
    worker = Worker(
        client,
        task_queue="netapp-activeiq-task-queue",
        workflows=[
            SVMCreationWorkflow,
            NFSShareProvisioningWorkflow,
            PerformanceMonitoringWorkflow,
            EventProcessingWorkflow,
            ComprehensiveStorageProvisioningWorkflow,
        ],
        activities=[
            validate_cluster_health,
            get_available_aggregates,
            create_svm,
            monitor_job_completion,
            create_nfs_share,
            get_performance_metrics,
            check_alert_thresholds,
            send_notification,
            get_system_events,
            acknowledge_event,
        ],
    )
    
    logger.info("Starting NetApp ActiveIQ Temporal worker...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
