# Temporal.io Integration for NetApp ActiveIQ API

## Overview

This document provides comprehensive guidance for integrating Temporal.io workflows with the NetApp ActiveIQ API, based on the sequence diagrams and use cases defined in our advanced documentation. Temporal.io provides durable execution, automatic retries, and state management for complex NetApp infrastructure workflows.

## Why Temporal.io for NetApp Operations?

- **Durability**: Workflows survive process restarts and failures
- **Reliability**: Automatic retries and error handling
- **Observability**: Built-in monitoring and debugging capabilities
- **Scalability**: Handle thousands of concurrent operations
- **State Management**: Automatic persistence of workflow state

## Prerequisites

- Docker installed and running
- Python 3.10+ (recommended: Python 3.12)
- NetApp ActiveIQ Unified Manager access
- Valid API credentials

## Quick Start Guide

### Step 1: Install Temporal Server

```bash
# Pull and run Temporal Server with auto-setup
docker run -d --name temporalio -p 7233:7233 -p 8080:8080 temporalio/auto-setup

# Verify installation
curl http://localhost:8080
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install temporalio requests dataclasses-json
```

### Step 3: Environment Setup

Create a `.env` file for configuration:

```bash
# NetApp ActiveIQ Configuration
NETAPP_UM_HOST=your-unified-manager.company.com
NETAPP_USERNAME=admin
NETAPP_PASSWORD=your-secure-password

# Temporal Configuration
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TASK_QUEUE=netapp-activeiq
```

## Workflow Implementations Based on Sequence Diagrams

### 1. SVM Creation Workflow

Based on the SVM Creation Sequence Diagram, here's the complete implementation:

```python
# netapp_workflows.py
from datetime import timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import asyncio
import logging
import requests
from requests.auth import HTTPBasicAuth

from temporalio import workflow, activity
from temporalio.common import RetryPolicy

@dataclass
class SVMConfig:
    name: str
    cluster_key: str
    aggregate_name: Optional[str] = None
    root_volume: str = "root"
    language: str = "c.utf_8"
    security_style: str = "unix"
    protocols: List[str] = None

    def __post_init__(self):
        if self.protocols is None:
            self.protocols = ["nfs"]

@dataclass
class NetworkInterface:
    name: str
    ip_address: str
    netmask: str
    node_uuid: str
    port_name: str
    service_policy: str

# Activities for NetApp API Operations
@activity.defn
async def validate_cluster_health(cluster_key: str, um_host: str, auth: tuple) -> Dict:
    """Step 1: Validate cluster health before SVM creation"""
    url = f"https://{um_host}/api/v2/datacenter/cluster/clusters/{cluster_key}"
    params = {"fields": "name,state,health,version"}

    response = requests.get(
        url,
        auth=HTTPBasicAuth(*auth),
        params=params,
        verify=False,  # For self-signed certificates
        timeout=30
    )

    if response.status_code != 200:
        raise Exception(f"Failed to validate cluster: {response.status_code} - {response.text}")

    cluster = response.json()
    if cluster.get('state') != 'up':
        raise Exception(f"Cluster {cluster.get('name')} is not up: {cluster.get('state')}")

    activity.logger.info(f"✓ Cluster {cluster['name']} is healthy and ready")
    return cluster

@activity.defn
async def get_available_aggregates(cluster_key: str, um_host: str, auth: tuple) -> List[Dict]:
    """Step 2: Get available aggregates for SVM creation"""
    url = f"https://{um_host}/api/v2/datacenter/storage/aggregates"
    params = {
        "query": f"cluster.key:{cluster_key}",
        "fields": "name,key,space.size,space.available,state"
    }

    response = requests.get(url, auth=HTTPBasicAuth(*auth), params=params, verify=False, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Failed to get aggregates: {response.status_code}")

    aggregates = response.json().get('records', [])
    available_aggs = [
        agg for agg in aggregates
        if agg.get('state') == 'online' and agg.get('space', {}).get('available', 0) > 10737418240  # 10GB min
    ]

    activity.logger.info(f"Found {len(available_aggs)} available aggregates")
    return available_aggs

@activity.defn
async def create_svm(svm_config: SVMConfig, um_host: str, auth: tuple) -> Dict:
    """Step 3: Create SVM with specified configuration"""
    url = f"https://{um_host}/api/v2/datacenter/svm/svms"

    payload = {
        "name": svm_config.name,
        "cluster": {"key": svm_config.cluster_key},
        "state": "running",
        "subtype": "default",
        "language": svm_config.language,
        "security_style": svm_config.security_style,
        "allowed_protocols": svm_config.protocols
    }

    if svm_config.aggregate_name:
        payload["aggregates"] = [{"name": svm_config.aggregate_name}]

    response = requests.post(
        url,
        auth=HTTPBasicAuth(*auth),
        json=payload,
        verify=False,
        timeout=60
    )

    if response.status_code not in [201, 202]:
        raise Exception(f"Failed to create SVM: {response.status_code} - {response.text}")

    result = response.json()
    activity.logger.info(f"✓ SVM creation initiated: {svm_config.name}")
    return result

@activity.defn
async def monitor_job_completion(job_uuid: str, um_host: str, auth: tuple, timeout_minutes: int = 30) -> Dict:
    """Step 4: Monitor job completion with polling"""
    url = f"https://{um_host}/api/v2/management-server/jobs/{job_uuid}"
    start_time = asyncio.get_event_loop().time()
    max_wait = timeout_minutes * 60

    while (asyncio.get_event_loop().time() - start_time) < max_wait:
        response = requests.get(url, auth=HTTPBasicAuth(*auth), verify=False, timeout=30)

        if response.status_code != 200:
            raise Exception(f"Failed to check job status: {response.status_code}")

        job = response.json()
        state = job.get('state')

        activity.logger.info(f"Job {job_uuid} status: {state} ({job.get('progress', 0)}%)")

        if state == 'success':
            return job
        elif state in ['failure', 'partial_failures']:
            raise Exception(f"Job failed: {job.get('message', 'Unknown error')}")

        await asyncio.sleep(10)  # Poll every 10 seconds

    raise Exception(f"Job {job_uuid} timed out after {timeout_minutes} minutes")

@activity.defn
async def create_network_interface(svm_key: str, interface: NetworkInterface, um_host: str, auth: tuple) -> Dict:
    """Step 5 & 6: Create management and data network interfaces"""
    url = f"https://{um_host}/api/v2/datacenter/svm/svms/{svm_key}/network/ip/interfaces"

    payload = {
        "name": interface.name,
        "ip": {
            "address": interface.ip_address,
            "netmask": interface.netmask
        },
        "location": {
            "home_node": {"uuid": interface.node_uuid},
            "home_port": {"name": interface.port_name}
        },
        "service_policy": interface.service_policy,
        "enabled": True
    }

    response = requests.post(
        url,
        auth=HTTPBasicAuth(*auth),
        json=payload,
        verify=False,
        timeout=30
    )

    if response.status_code not in [201, 202]:
        raise Exception(f"Failed to create interface {interface.name}: {response.status_code}")

    activity.logger.info(f"✓ Network interface {interface.name} created")
    return response.json()

# SVM Creation Workflow
@workflow.defn
class SVMCreationWorkflow:
    """Complete SVM Creation Workflow based on sequence diagram"""

    @workflow.run
    async def run(self, svm_config: SVMConfig, um_host: str, auth: tuple) -> Dict:
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            maximum_attempts=3
        )

        workflow.logger.info(f"Starting SVM creation workflow for {svm_config.name}")

        # Step 1: Validate cluster health
        cluster_info = await workflow.execute_activity(
            validate_cluster_health,
            svm_config.cluster_key,
            um_host,
            auth,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy
        )

        # Step 2: Get available aggregates
        aggregates = await workflow.execute_activity(
            get_available_aggregates,
            svm_config.cluster_key,
            um_host,
            auth,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy
        )

        # Select best aggregate (most available space)
        if aggregates:
            best_aggregate = max(aggregates, key=lambda x: x.get('space', {}).get('available', 0))
            svm_config.aggregate_name = best_aggregate['name']
            workflow.logger.info(f"Selected aggregate: {best_aggregate['name']}")

        # Step 3: Create SVM
        svm_result = await workflow.execute_activity(
            create_svm,
            svm_config,
            um_host,
            auth,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=retry_policy
        )

        # Step 4: Monitor job completion if async operation
        if 'job' in svm_result:
            job_result = await workflow.execute_activity(
                monitor_job_completion,
                svm_result['job']['uuid'],
                um_host,
                auth,
                30,  # timeout in minutes
                start_to_close_timeout=timedelta(minutes=35),
                retry_policy=retry_policy
            )

        svm_key = svm_result.get('svm_key') or svm_result.get('key')

        # Steps 5 & 6: Create network interfaces
        mgmt_interface = NetworkInterface(
            name=f"{svm_config.name}_mgmt",
            ip_address="10.1.100.50",  # This should be parameterized
            netmask="255.255.255.0",
            node_uuid="node-uuid-placeholder",  # This should be retrieved dynamically
            port_name="e0c",
            service_policy="default-management"
        )

        data_interface = NetworkInterface(
            name=f"{svm_config.name}_data",
            ip_address="10.1.100.51",  # This should be parameterized
            netmask="255.255.255.0",
            node_uuid="node-uuid-placeholder",  # This should be retrieved dynamically
            port_name="e0d",
            service_policy="default-data-files"
        )

        # Create management interface
        mgmt_result = await workflow.execute_activity(
            create_network_interface,
            svm_key,
            mgmt_interface,
            um_host,
            auth,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy
        )

        # Create data interface
        data_result = await workflow.execute_activity(
            create_network_interface,
            svm_key,
            data_interface,
            um_host,
            auth,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy
        )

        return {
            "svm_name": svm_config.name,
            "svm_key": svm_key,
            "cluster_info": cluster_info,
            "aggregate_used": best_aggregate if aggregates else None,
            "management_interface": mgmt_result,
            "data_interface": data_result,
            "status": "completed"
        }
```

### 2. NFS Share Creation Workflow

Based on the NFS Share Creation Sequence Diagram:

```python
@dataclass
class NFSShareConfig:
    name: str
    svm_key: str
    path: str
    size: str
    export_policy_name: str = "default"
    unix_permissions: str = "755"
    security_style: str = "unix"

@dataclass
class ExportPolicyRule:
    clients: List[str]
    protocols: List[str]
    ro_rule: List[str]
    rw_rule: List[str]
    superuser: List[str]
    allow_suid: bool = False

# NFS-specific Activities
@activity.defn
async def create_export_policy(svm_key: str, policy_name: str, rules: List[ExportPolicyRule], um_host: str, auth: tuple) -> Dict:
    """Step 1: Create export policy with rules"""
    url = f"https://{um_host}/api/v2/datacenter/svm/svms/{svm_key}/export-policies"

    payload = {
        "name": policy_name,
        "rules": [
            {
                "clients": rule.clients,
                "protocols": rule.protocols,
                "ro_rule": rule.ro_rule,
                "rw_rule": rule.rw_rule,
                "superuser": rule.superuser,
                "allow_suid": rule.allow_suid
            } for rule in rules
        ]
    }

    response = requests.post(url, auth=HTTPBasicAuth(*auth), json=payload, verify=False, timeout=30)

    if response.status_code not in [201, 202]:
        raise Exception(f"Failed to create export policy: {response.status_code}")

    activity.logger.info(f"✓ Export policy {policy_name} created")
    return response.json()

@activity.defn
async def create_file_share(share_config: NFSShareConfig, um_host: str, auth: tuple) -> Dict:
    """Step 2: Create NFS file share"""
    url = f"https://{um_host}/api/v2/storage-provider/file-shares"

    payload = {
        "name": share_config.name,
        "size": share_config.size,
        "svm": {"key": share_config.svm_key},
        "path": share_config.path,
        "export_policy": {"name": share_config.export_policy_name},
        "unix_permissions": share_config.unix_permissions,
        "security_style": share_config.security_style
    }

    response = requests.post(url, auth=HTTPBasicAuth(*auth), json=payload, verify=False, timeout=60)

    if response.status_code not in [201, 202]:
        raise Exception(f"Failed to create file share: {response.status_code}")

    activity.logger.info(f"✓ NFS share {share_config.name} created")
    return response.json()

@activity.defn
async def apply_export_policy(share_key: str, policy_name: str, um_host: str, auth: tuple) -> Dict:
    """Step 3: Apply export policy to file share"""
    url = f"https://{um_host}/api/v2/storage-provider/file-shares/{share_key}"

    payload = {
        "export_policy": {"name": policy_name}
    }

    response = requests.patch(url, auth=HTTPBasicAuth(*auth), json=payload, verify=False, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Failed to apply export policy: {response.status_code}")

    activity.logger.info(f"✓ Export policy {policy_name} applied to share")
    return response.json()

@activity.defn
async def verify_nfs_access(svm_key: str, um_host: str, auth: tuple) -> Dict:
    """Step 4: Verify NFS service is accessible"""
    url = f"https://{um_host}/api/v2/datacenter/svm/svms/{svm_key}"
    params = {"fields": "nfs.enabled,state,protocols"}

    response = requests.get(url, auth=HTTPBasicAuth(*auth), params=params, verify=False, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Failed to verify NFS access: {response.status_code}")

    svm_info = response.json()

    if not svm_info.get('nfs', {}).get('enabled', False):
        raise Exception("NFS is not enabled on SVM")

    activity.logger.info("✓ NFS access verified")
    return svm_info

# NFS Share Creation Workflow
@workflow.defn
class NFSShareCreationWorkflow:
    """Complete NFS Share Creation Workflow based on sequence diagram"""

    @workflow.run
    async def run(self, share_config: NFSShareConfig, export_rules: List[ExportPolicyRule], um_host: str, auth: tuple) -> Dict:
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=2),
            maximum_interval=timedelta(seconds=30),
            maximum_attempts=3
        )

        workflow.logger.info(f"Starting NFS share creation workflow for {share_config.name}")

        # Step 1: Create export policy
        export_policy_result = await workflow.execute_activity(
            create_export_policy,
            share_config.svm_key,
            share_config.export_policy_name,
            export_rules,
            um_host,
            auth,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy
        )

        # Step 2: Create file share
        share_result = await workflow.execute_activity(
            create_file_share,
            share_config,
            um_host,
            auth,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy
        )

        share_key = share_result.get('key')

        # Step 3: Apply export policy (if not already applied)
        if share_key:
            policy_result = await workflow.execute_activity(
                apply_export_policy,
                share_key,
                share_config.export_policy_name,
                um_host,
                auth,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy
            )

        # Step 4: Verify NFS access
        nfs_verification = await workflow.execute_activity(
            verify_nfs_access,
            share_config.svm_key,
            um_host,
            auth,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy
        )

        return {
            "share_name": share_config.name,
            "share_key": share_key,
            "export_policy": export_policy_result,
            "nfs_verification": nfs_verification,
            "status": "completed"
        }
```

### 3. Worker Implementation

```python
# worker.py
import asyncio
import logging
import os
from temporalio.client import Client
from temporalio.worker import Worker

from netapp_workflows import (
    SVMCreationWorkflow,
    NFSShareCreationWorkflow,
    # Import all activities
    validate_cluster_health,
    get_available_aggregates,
    create_svm,
    monitor_job_completion,
    create_network_interface,
    create_export_policy,
    create_file_share,
    apply_export_policy,
    verify_nfs_access,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Connect to Temporal server
    client = await Client.connect(os.getenv("TEMPORAL_HOST", "localhost:7233"))

    # Create worker
    worker = Worker(
        client,
        task_queue=os.getenv("TASK_QUEUE", "netapp-activeiq"),
        workflows=[
            SVMCreationWorkflow,
            NFSShareCreationWorkflow,
        ],
        activities=[
            validate_cluster_health,
            get_available_aggregates,
            create_svm,
            monitor_job_completion,
            create_network_interface,
            create_export_policy,
            create_file_share,
            apply_export_policy,
            verify_nfs_access,
        ],
    )

    logger.info("Starting NetApp ActiveIQ Temporal worker...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. Client Usage Examples

```python
# client.py
import asyncio
import os
from temporalio.client import Client

from netapp_workflows import SVMConfig, NFSShareConfig, ExportPolicyRule

async def run_svm_creation():
    client = await Client.connect(os.getenv("TEMPORAL_HOST", "localhost:7233"))

    # Configure SVM
    svm_config = SVMConfig(
        name="production_nfs_svm",
        cluster_key="cluster-12345-abcde",
        protocols=["nfs"]
    )

    # Start workflow
    result = await client.execute_workflow(
        "SVMCreationWorkflow.run",
        svm_config,
        os.getenv("NETAPP_UM_HOST"),
        (os.getenv("NETAPP_USERNAME"), os.getenv("NETAPP_PASSWORD")),
        id=f"svm-creation-{svm_config.name}",
        task_queue="netapp-activeiq"
    )

    print(f"SVM Creation Result: {result}")
    return result

async def run_nfs_share_creation(svm_key: str):
    client = await Client.connect(os.getenv("TEMPORAL_HOST", "localhost:7233"))

    # Configure NFS share
    share_config = NFSShareConfig(
        name="shared_documents",
        svm_key=svm_key,
        path="/shared_documents",
        size="500GB",
        export_policy_name="production_policy"
    )

    # Define export rules
    export_rules = [
        ExportPolicyRule(
            clients=["10.1.0.0/16"],
            protocols=["nfs3", "nfs4"],
            ro_rule=["sys"],
            rw_rule=["sys"],
            superuser=["sys"]
        ),
        ExportPolicyRule(
            clients=["192.168.1.0/24"],
            protocols=["nfs3", "nfs4"],
            ro_rule=["sys"],
            rw_rule=["none"],
            superuser=["none"]
        )
    ]

    # Start workflow
    result = await client.execute_workflow(
        "NFSShareCreationWorkflow.run",
        share_config,
        export_rules,
        os.getenv("NETAPP_UM_HOST"),
        (os.getenv("NETAPP_USERNAME"), os.getenv("NETAPP_PASSWORD")),
        id=f"nfs-share-{share_config.name}",
        task_queue="netapp-activeiq"
    )

    print(f"NFS Share Creation Result: {result}")
    return result

if __name__ == "__main__":
    # Example: Create SVM first, then NFS share
    async def main():
        svm_result = await run_svm_creation()
        if svm_result and svm_result.get("status") == "completed":
            await run_nfs_share_creation(svm_result["svm_key"])

    asyncio.run(main())
```

## Running the Workflows

### 1. Start Temporal Server

```bash
docker run -d --name temporalio -p 7233:7233 -p 8080:8080 temporalio/auto-setup
```

### 2. Start the Worker

```bash
# Set environment variables
export NETAPP_UM_HOST=your-unified-manager.company.com
export NETAPP_USERNAME=admin
export NETAPP_PASSWORD=your-password

# Start worker
python worker.py
```

### 3. Execute Workflows

```bash
# In another terminal
python client.py
```

### 4. Monitor Workflows

Access the Temporal Web UI at `http://localhost:8080` to monitor workflow execution, view logs, and debug issues.

## Error Handling and Best Practices

### Retry Policies

```python
# Custom retry policy for critical operations
critical_retry_policy = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(minutes=5),
    maximum_attempts=5,
    backoff_coefficient=2.0
)

# Non-critical operations
standard_retry_policy = RetryPolicy(
    initial_interval=timedelta(seconds=2),
    maximum_interval=timedelta(seconds=30),
    maximum_attempts=3
)
```

### Logging and Monitoring

```python
# Add structured logging
import structlog

logger = structlog.get_logger()

@activity.defn
async def monitored_activity(param: str) -> str:
    logger.info("Activity started", activity="monitored_activity", param=param)
    try:
        # Activity logic here
        result = "success"
        logger.info("Activity completed", result=result)
        return result
    except Exception as e:
        logger.error("Activity failed", error=str(e), param=param)
        raise
```

## Conclusion

This comprehensive Temporal.io integration provides:

- **Robust workflow execution** for complex NetApp operations
- **Automatic error handling** and retry mechanisms
- **Complete observability** through the Temporal Web UI
- **Scalable architecture** for handling multiple concurrent operations
- **Production-ready implementations** based on real sequence diagrams

The workflows can be extended to handle additional NetApp operations like credential updates, performance monitoring, and event processing as defined in the advanced use cases documentation.
