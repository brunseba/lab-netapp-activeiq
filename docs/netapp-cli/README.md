# NetApp ActiveIQ CLI Tool

A comprehensive command-line interface to interact with ActiveIQ Server. This CLI tool provides management capabilities for NetApp storage systems through the ActiveIQ API, including storage provisioning, monitoring, snapshot management, and more.

## Features

- **Authentication Management**: Configure and test API credentials
- **Cluster Management**: List and monitor NetApp clusters
- **Volume Operations**: Create, list, and manage storage volumes
- **Snapshot Management**: Create, delete, and manage volume snapshots
- **LUN Operations**: Manage and expand LUNs
- **File Share Management**: Provision and manage NFS/CIFS file shares
- **Monitoring**: Performance monitoring and health checks
- **Multiple Output Formats**: Table, JSON, and YAML output support
- **Flexible Configuration**: YAML configuration files and environment variables

## Installation

### Prerequisites

- Python 3.11 or higher
- `uv` package manager

### Install from Source

1. Clone the repository:

```bash
git clone <repository-url>
cd netapp-cli
```

2. Install using uv:

```bash
uv sync
```

3. Install the CLI:

```bash
uv pip install -e .
```

## Quick Start

### 1. Configure Authentication

Create a sample configuration file:

```bash
netapp auth sample-config
```

Edit the generated `netapp-cli.yaml` file with your ActiveIQ Server credentials:

```yaml
netapp:
  host: your-activeiq-server.example.com
  username: admin
  password: your-password
  verify_ssl: true
  timeout: 30
  api_version: v1
```

### 2. Test Connection

```bash
netapp auth test
```

### 3. Basic Usage Examples

List clusters:

```bash
netapp cluster list
```

List volumes in an SVM:

```bash
netapp volume list --svm svm1
```

Create a snapshot:

```bash
netapp snapshot create volume1 snap1 --svm svm1 --comment "Manual backup"
```

Monitor cluster performance:

```bash
netapp monitor cluster-performance
```

## Command Reference

### Authentication Commands

```bash
netapp auth configure          # Interactive configuration setup
netapp auth test              # Test current configuration
netapp auth status            # Show configuration status
netapp auth clear             # Clear stored configuration
netapp auth sample-config     # Create sample configuration file
```

### Cluster Management

```bash
netapp cluster list                    # List all clusters
netapp cluster show <cluster_key>     # Show cluster details
netapp cluster performance            # Show performance analytics
netapp cluster svms                   # List all SVMs
netapp cluster aggregates            # List all aggregates
```

### Volume Management

```bash
netapp volume list --svm <svm_name>              # List volumes
netapp volume show <volume_name> --svm <svm>     # Show volume details
netapp volume list-volumes --name <pattern>      # List with filtering
```

### Snapshot Management

```bash
netapp snapshot list <volume_name>                           # List snapshots
netapp snapshot create <volume> <snapshot_name>              # Create snapshot
netapp snapshot delete <volume> <snapshot_name>              # Delete snapshot
netapp snapshot list-policies                                # List policies
netapp snapshot create-policy <name> --svm <svm> --schedule daily:7
```

### LUN Management

```bash
netapp lun list --svm <svm_name>        # List LUNs
netapp lun show <lun_key>               # Show LUN details
netapp lun expand <lun_key> <new_size>  # Expand LUN
```

### File Share Management

```bash
netapp fileshare list --svm <svm_name>                    # List file shares
netapp fileshare create <name> --svm <svm> --aggregate <aggr> --size <bytes>
netapp fileshare delete <fileshare_key>                   # Delete file share
netapp fileshare show <fileshare_key>                     # Show details
```

### Monitoring Commands

```bash
netapp monitor cluster-performance     # Cluster performance metrics
netapp monitor volume-performance      # Volume performance and usage
netapp monitor events                  # System events and alerts
netapp monitor jobs                    # Background jobs
netapp monitor health                  # Overall system health
```

## Object Naming Convention

The NetApp ActiveIQ CLI follows a standardized naming convention for all managed objects to ensure consistency, clarity, and ease of management across environments.

### General Naming Guidelines

- Use **lowercase letters** with hyphens `-` to separate words
- Use **descriptive names** to clearly indicate the object's purpose and characteristics
- Incorporate the **object type prefix** for easy identification
- Include **environment name** to distinguish between deployment environments
- Add **numerical ID** for unique identification and easier management

### Naming Format Structure

```
{object-type}-{environment}-{context}-{purpose}-{id}
```

### Environment Codes

- `prod` - Production environment
- `stage` - Staging environment
- `test` - Testing environment
- `dev` - Development environment
- `qa` - Quality assurance environment

### Object-Specific Naming Conventions

#### Clusters

- **Format**: `cluster-{env}-{location}-{purpose}-{id}`
- **Example**: `cluster-prod-us-west-analytics-001`
- **Components**:
  - `env`: Environment (prod, dev, test, stage, qa)
  - `location`: Geographic or logical location (us-west, eu-central, dc1)
  - `purpose`: Primary use case (analytics, backup, archive)
  - `id`: 3-digit numerical identifier (001, 002, etc.)

#### Volumes

- **Format**: `vol-{env}-{svm-name}-{purpose}-{id}`
- **Example**: `vol-dev-finance-reports-002`
- **Components**:
  - `env`: Environment identifier
  - `svm-name`: Storage Virtual Machine name
  - `purpose`: Volume purpose (reports, logs, data, backup)
  - `id`: 3-digit numerical identifier

#### Snapshots

- **Format**: `snap-{env}-{volume-name}-{date}-{id}`
- **Example**: `snap-test-reports-20250730-003`
- **Components**:
  - `env`: Environment identifier
  - `volume-name`: Associated volume name (without vol- prefix)
  - `date`: Creation date in YYYYMMDD format
  - `id`: 3-digit numerical identifier

#### LUNs

- **Format**: `lun-{env}-{application}-{size}-{id}`
- **Example**: `lun-prod-oracle-500gb-004`
- **Components**:
  - `env`: Environment identifier
  - `application`: Target application (oracle, mysql, vmware)
  - `size`: Storage size with unit (500gb, 2tb)
  - `id`: 3-digit numerical identifier

#### File Shares

- **Format**: `share-{env}-{svm-name}-{protocol}-{access}-{id}`
- **Example**: `share-qa-research-nfs-readonly-005`
- **Components**:
  - `env`: Environment identifier
  - `svm-name`: Storage Virtual Machine name
  - `protocol`: Protocol type (nfs, cifs, smb)
  - `access`: Access type (readonly, readwrite, shared)
  - `id`: 3-digit numerical identifier

#### Snapshot Policies

- **Format**: `policy-{env}-{frequency}-{category}-{id}`
- **Example**: `policy-stage-daily-backup-006`
- **Components**:
  - `env`: Environment identifier
  - `frequency`: Backup frequency (hourly, daily, weekly, monthly)
  - `category`: Policy category (backup, archive, replication)
  - `id`: 3-digit numerical identifier

### Usage Examples

```bash
# Create volume following naming convention
netapp volume create vol-prod-finance-reports-001 --svm finance-svm --size 100GB

# Create snapshot with standardized name
netapp snapshot create vol-prod-finance-reports-001 snap-prod-reports-20250730-001

# List objects with naming pattern
netapp volume list --name "vol-prod-*"
netapp snapshot list --name "snap-test-*"
```

### Benefits of Standardized Naming

1. **Environment Identification**: Quickly identify which environment an object belongs to
2. **Logical Grouping**: Easy filtering and searching by environment, purpose, or type
3. **Automated Management**: Enables scripted operations and automation
4. **Disaster Recovery**: Clear identification for backup and recovery procedures
5. **Compliance**: Supports audit requirements and governance policies
6. **Team Collaboration**: Consistent naming reduces confusion across teams

### Validation

The CLI includes built-in validation to ensure naming conventions are followed:

```bash
# Enable naming convention validation
netapp config set validate-naming true

# Check existing objects against naming standards
netapp validate naming-convention
```

## Configuration

### Configuration File

The CLI looks for configuration files in the following locations:

1. `~/.netapp-cli/netapp-cli.yaml` (preferred location)
2. `~/.netapp-cli/netapp-cli.yml`
3. `netapp-cli.yaml` (current directory)
4. `netapp-cli.yml` (current directory)
5. `~/.netapp-cli.yaml`
6. `~/.netapp-cli.yml`
7. `~/.config/netapp-cli/config.yaml`
8. `~/.config/netapp-cli/config.yml`

### Environment Variables

You can also configure the CLI using environment variables:

```bash
export NETAPP_HOST=your-activeiq-server.example.com
export NETAPP_USERNAME=admin
export NETAPP_PASSWORD=your-password
export NETAPP_VERIFY_SSL=true
export NETAPP_TIMEOUT=30
export NETAPP_API_VERSION=v1
```

### Command Line Options

Global options available for all commands:

- `-c, --config PATH`: Path to configuration file
- `-v, --verbose`: Enable verbose output
- `-o, --output [table|json|yaml]`: Output format

## Output Formats

The CLI supports three output formats:

### Table (Default)

```bash
netapp cluster list
```

### JSON

```bash
netapp cluster list --output json
```

### YAML

```bash
netapp cluster list --output yaml
```

## Error Handling

The CLI provides comprehensive error handling with informative messages:

- **Authentication errors**: Clear messages for credential issues
- **Network errors**: Timeout and connection error handling
- **API errors**: Detailed error messages from the ActiveIQ API
- **Validation errors**: Input validation with helpful suggestions

## Development

### Setting up Development Environment

1. Clone the repository
2. Install development dependencies:

```bash
uv sync --dev
```

3. Run tests:

```bash
uv run pytest
```

4. Format code:

```bash
uv run black .
uv run ruff check .
```

### Project Structure

```
netapp_cli/
├── __init__.py
├── main.py              # Main CLI entry point
├── commands/            # Command modules
│   ├── auth.py
│   ├── cluster.py
│   ├── volume.py
│   ├── snapshot.py
│   ├── lun.py
│   ├── fileshare.py
│   └── monitor.py
└── utils/               # Utility modules
    ├── config.py        # Configuration management
    ├── api_client.py    # ActiveIQ API client
    └── output.py        # Output formatting
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the command help: `netapp <command> --help`
3. Use verbose mode for debugging: `netapp -v <command>`

## API Compatibility

This CLI is designed to work with NetApp ActiveIQ Unified Manager API. It has been tested with:

- ActiveIQ Unified Manager 9.x
- ONTAP REST API

## Version History

- **0.1.0**: Initial release with core functionality
  - Authentication management
  - Cluster, volume, and snapshot operations
  - LUN and file share management
  - Performance monitoring
  - Multiple output formats
