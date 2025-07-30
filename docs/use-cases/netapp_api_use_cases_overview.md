# NetApp ActiveIQ API - Use Cases Overview

This document provides an overview of the use cases for NetApp ActiveIQ automation, now organized into specialized categories for better navigation and implementation guidance.

## 📁 Use Cases Organization

The use cases have been reorganized into two main categories:

### 🌐 [NetApp API Use Cases](netapp-api/overview.md)

**Standard Storage Operations** - Core NetApp ActiveIQ API functionality:

- **Storage provisioning** and management (NFS file shares, LUN expansion)

- **Resource management** (decommissioning, cleanup procedures)

- **Performance monitoring** and analytics

- **Tagging & annotation** workflows (event annotation, SVM tagging, volume name tags)

- **Metadata management** (generic metadata attachment, search by metadata)

- **Infrastructure operations** and maintenance

### 🔧 [MCP Tools Use Cases](mcp-tools/overview.md)

**Model Context Protocol Integration** - Advanced DevOps workflows with MCP enhancement:

- **Backup & Recovery** with MCP-enhanced context and AI-assisted recovery

- **Capacity Planning** with AI forecasting and automated scaling

- **Event Management** with intelligent correlation and automated workflows

- **Performance Analysis** with AI-powered insights and predictive analytics

- **SVM Management** with automated provisioning and AI optimization

- **Volume Operations** with intelligent monitoring and automated optimization

## Authentication

All NetApp ActiveIQ API requests require **HTTP Basic Authentication**. Each automation script must:

1. Obtain valid credentials (username/password) with appropriate permissions
2. Include the `Authorization` header in every API request
3. Handle authentication failures gracefully

## Quick Reference - Use Cases by Category

### 1. [Provisioning a New NFS File Share](netapp-api/provision_nfs_fileshare.md)

**Objective**: Automate the creation of new NFS file shares for clients.

**Key Steps**:

- Discover available clusters and SVMs
- Select appropriate aggregates with sufficient space
- Create the file share with proper export policies
- Monitor the creation job until completion

**Common Errors**: Authentication failures, insufficient space, invalid export policies, job failures.

### 2. [Decommissioning a File Share](netapp-api/decommission_fileshare.md)

**Objective**: Safely remove file shares that are no longer needed.

**Key Steps**:

- Locate the target file share
- Verify no active connections (optional)
- Delete the file share
- Monitor the deletion job

**Common Errors**: File share not found, permission issues, active connections, deletion constraints.

### 3. [Expanding a LUN](netapp-api/expand_lun.md)

**Objective**: Increase the size of existing LUNs to meet growing storage requirements.

**Key Steps**:

- Locate the target LUN
- Validate the new size requirements
- Expand the LUN
- Monitor the expansion job
- (Optional) Provide guidance for host-side expansion

**Common Errors**: LUN not found, insufficient space, invalid size parameters, LUN state issues.

### 4. [Monitoring Cluster Performance](netapp-api/monitor_cluster_performance.md)

**Objective**: Continuously monitor cluster performance metrics for proactive management.

**Key Steps**:

- Identify target clusters
- Retrieve performance metrics for specified time intervals
- Process and analyze the metrics data
- Generate alerts or reports as needed

**Common Errors**: Cluster not found, invalid time intervals, metrics unavailable, rate limiting.

### 5. [Annotating an Event](netapp-api/annotate_event.md)

**Objective**: Add metadata annotations to events for enhanced tracking, categorization, and automation workflows.

**Key Steps**:

- Search for events using specific criteria (severity, state, resource type)
- Select events that require annotation
- Add structured annotations using key-value pairs
- Verify the annotation was applied successfully

**Common Errors**: Event not found, invalid annotation format, permission issues, concurrent modification conflicts.

### 6. [Tagging a Volume with `name_tag`](netapp-api/tag_volume_with_nametag.md)

**Objective**: Use `name_tag` to create consistently named volumes during LUN creation for better organization and searchability.

**Key Steps**:

- Discover available SVMs for LUN creation
- Create a LUN with a specific `volume.name_tag` parameter
- Monitor the LUN creation job until completion
- Verify the volume was created with the expected name derived from the tag

**Common Errors**: Invalid name_tag format, volume name conflicts, insufficient space, SVM not found, job failures.

### 7. [Tagging an SVM via Event Annotation](netapp-api/tag_svm_with_event_annotation.md)

**Objective**: Add custom metadata tags to SVMs by creating associated events with annotations, enabling SVM categorization and management.

**Key Steps**:

- Locate the target SVM using discovery endpoints
- Create a new event associated with the SVM
- Add structured annotations to the event (e.g., group, owner, project metadata)
- Monitor the event creation job until completion
- Verify the annotation was applied successfully

**Common Errors**: SVM not found, invalid event payload, job failures, annotation format issues.

### 8. [Attaching Metadata to any Object](netapp-api/attach_metadata_to_object.md)

**Objective**: Provide a universal mechanism for attaching custom metadata to any object within ActiveIQ Unified Manager using the console's event annotation capabilities.

**Key Steps**:

- User selects an object in the ActiveIQ console
- User initiates an "Add Annotation" action
- Console creates an event associated with the object and adds the metadata as an annotation
- User can view all annotations for an object in the console

**Common Errors**: Object not found, invalid metadata format, permission denied, job failures.

### 9. [Searching for Objects by Metadata](netapp-api/search_object_by_metadata.md)

**Objective**: Enable powerful search capabilities to find objects based on their attached metadata tags, supporting both API-based automation and console-based user interfaces.

**Key Steps**:

- Search events using annotation filters (e.g., `owner:team_a`, `environment:production`)
- Parse event results to extract unique resource keys
- Retrieve full object details for each matching resource
- Present categorized search results grouped by object type
- Support advanced search patterns for compliance, cost tracking, and resource management

**Common Errors**: No matching results, invalid search syntax, deleted resources, pagination handling.

## NetApp ActiveIQ Administrative Philosophy

NetApp ActiveIQ Unified Manager follows an **event-driven administrative approach** that provides comprehensive metadata management capabilities through its built-in event system. This philosophy aligns with enterprise requirements for:

### Audit and Compliance

- **Complete Audit Trail**: All metadata changes are recorded as events with timestamps and user attribution
- **Regulatory Compliance**: Events provide the documentation trail required for SOX, GDPR, and other compliance frameworks
- **Change Management**: Integration with ITSM systems through event-based workflows

### Enterprise Integration

- **RBAC Integration**: Leverages existing role-based access control for metadata management
- **Workflow Automation**: Events can trigger automated responses and notifications
- **Reporting and Analytics**: Metadata can be aggregated and analyzed through the event system

### Operational Excellence

- **Centralized Management**: All metadata is managed through the same interface used for monitoring and administration
- **Consistency**: Standardized approach ensures uniform metadata handling across all object types
- **Scalability**: Event-based system scales with enterprise growth and complexity

## Tagging and Labeling Approaches

NetApp ActiveIQ API provides multiple approaches for adding labels/tags to objects:

### Event Annotations

- **Purpose**: Add metadata to events for categorization, workflow integration, and reporting
- **Format**: Free-form string (recommended: key-value pairs like `priority:high,team:storage`)
- **API Endpoint**: `PATCH /management-server/events/{key}`
- **Use Cases**:
  - ITSM integration (ticket numbers, workflow IDs)
  - Priority classification and routing
  - Team assignment and responsibility tracking
  - Compliance and audit metadata

### Volume Name Tags

- **Purpose**: Create consistent volume naming during LUN creation
- **Format**: String that becomes part of the volume name (e.g., `sample_volume` → `NSLM_sample_volume`)
- **API Endpoint**: `POST /storage-provider/luns` with `volume.name_tag` parameter
- **Use Cases**:
  - Standardized naming conventions
  - Environment identification (dev, test, prod)
  - Application or project grouping
  - Cost center or department tracking

### Comparison

| Aspect            | Event Annotations            | Volume Name Tags                   |
| ----------------- | ---------------------------- | ---------------------------------- |
| **Timing**        | Applied after event creation | Applied during LUN/volume creation |
| **Scope**         | Events only                  | Volumes (via LUN creation)         |
| **Format**        | Free-form string             | Naming convention string           |
| **Persistence**   | Stored as metadata           | Embedded in volume name            |
| **Searchability** | Via API filters              | Via volume name searches           |
| **Mutability**    | Can be modified              | Fixed after creation (immutable)   |

## General Error Handling Strategies

### Network and Connectivity

- **Timeout Errors**: Implement exponential backoff retry logic
- **Connection Errors**: Verify network connectivity and API endpoint availability
- **Rate Limiting (429)**: Implement request throttling and backoff strategies

### Authentication and Authorization

- **401 Unauthorized**: Verify credentials and re-authenticate if necessary
- **403 Forbidden**: Check user permissions and role assignments

### Resource Management

- **404 Not Found**: Implement resource discovery and validation logic
- **400 Bad Request**: Parse error messages and provide user-friendly feedback
- **409 Conflict**: Handle resource state conflicts gracefully

### Asynchronous Operations

- **Job Monitoring**: Implement polling logic with appropriate intervals
- **Job Failures**: Retrieve detailed error information from failed jobs
- **Timeout Handling**: Set reasonable timeouts for long-running operations

## Best Practices

### Security

- Store credentials securely (environment variables, secure vaults)
- Use service accounts with minimal required permissions
- Implement proper credential rotation

### Reliability

- Implement idempotent operations where possible
- Use circuit breaker patterns for external dependencies
- Log all operations for troubleshooting and audit purposes

### Performance

- Cache frequently accessed data (clusters, SVMs, etc.)
- Implement connection pooling for high-frequency operations
- Use appropriate request batching where supported

### Monitoring

- Track API response times and error rates
- Monitor job completion rates and failure patterns
- Implement health checks for the automation system

## Implementation Tools

The automation scripts can be implemented using various technologies:

- **Python**: Using `requests` library for HTTP operations
- **PowerShell**: Using `Invoke-RestMethod` cmdlets
- **Bash/curl**: For simple operations and testing
- **Go**: For high-performance, concurrent operations
- **Terraform**: For infrastructure-as-code approaches

## Integration Patterns

These use cases can be integrated into larger automation workflows:

- **CI/CD Pipelines**: Provision storage as part of application deployment
- **Monitoring Systems**: Integrate performance monitoring with alerting platforms
- **ITSM Tools**: Trigger storage operations from service request workflows
- **Infrastructure as Code**: Define storage resources in declarative formats

## Next Steps

For each use case, consider:

1. **Implementation**: Develop the automation scripts using your preferred technology
2. **Testing**: Validate the scripts in a test environment
3. **Monitoring**: Implement logging and alerting for the automation
4. **Documentation**: Create operational runbooks and troubleshooting guides
5. **Integration**: Connect the automation to your existing workflows and systems
