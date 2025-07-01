# NetApp Temporal Workflows

Temporal.io workflows for NetApp ActiveIQ infrastructure management, providing durable execution for complex storage operations.

## Features

- **Durable Workflows**: Fault-tolerant execution with automatic retries
- **SVM Management**: Automated Storage Virtual Machine creation and configuration
- **NFS Provisioning**: Complete NFS share provisioning with validation
- **Performance Monitoring**: Continuous monitoring with alerting
- **Event Processing**: Automated event handling and notifications

## Workflows

- **SVMCreationWorkflow**: Creates SVMs with cluster validation
- **NFSShareProvisioningWorkflow**: Provisions NFS shares
- **PerformanceMonitoringWorkflow**: Monitors cluster performance
- **EventProcessingWorkflow**: Processes system events
- **ComprehensiveStorageProvisioningWorkflow**: End-to-end storage setup

## Installation

```bash
# Install with uv
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"
```

## Usage

```bash
# Start the Temporal worker
netapp-temporal-worker

# Or run directly
python -m netapp_temporal_workflows.temporal_worker
```

## Prerequisites

- Running Temporal.io server
- NetApp ActiveIQ Unified Manager access

## Configuration

Configure Temporal connection:

```bash
export TEMPORAL_HOST="localhost:7233"
export TEMPORAL_NAMESPACE="default"
export NETAPP_API_ENDPOINT="https://your-netapp-aiqum.example.com/api"
```

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .
```
