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
