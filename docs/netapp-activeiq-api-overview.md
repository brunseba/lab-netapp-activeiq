# NetApp ActiveIQ API - Overview

## Introduction

This documentation provides an overview of the NetApp ActiveIQ REST API based on the analysis of external data sources. The NetApp ActiveIQ API suite provides programmatic access to manage, monitor, and extract data from NetApp storage environments through **Active IQ Unified Manager** and **Digital Advisor**.

## API Information

- **Title**: Active IQ Unified Manager - API Documentation
- **Version**: v2
- **Base Path**: `/api`
- **Support**: NetApp Support - https://mysupport.netapp.com

## Key Features

### RESTful Design
- Follows REST principles
- Supports standard HTTP methods (GET, POST, PATCH, DELETE)
- Full CRUD operations on storage resources
- Content-Type: `application/json`

### Comprehensive Coverage
- **Over 100 endpoints** grouped into 20+ service areas
- Coverage includes:
  - System information
  - Storage efficiency
  - Performance monitoring
  - Health status
  - Upgrades management
  - Backup operations
  - Access endpoints
  - Performance service levels
  - Workload management

### Use Cases
- Automate monitoring and management
- Integration with ticketing/reporting systems
- Build custom dashboards
- Manage storage resources programmatically
- Risk detection and health checks
- Data extraction for analytics

## Authentication & Access

### Endpoint Structure
```
https://<hostname>:<port>/api/v2/<service>/<resource>
```

**Default Configuration:**
- Port: 443 (HTTPS)
- Authentication: HTTP Basic Authentication (username/password)
- SSL: Supports self-signed or custom SSL certificates
- User types: Both local and LDAP users supported

### Required Roles
To access the API documentation and endpoints, users must have one of the following roles:
- Operator
- Storage Administrator
- Application Administrator

## API Documentation Access

### Interactive Documentation (Swagger UI)
Access the interactive API documentation at:
```
https://<Unified_Manager_IP_or_FQDN>/apidocs/
```
or
```
https://<Unified_Manager_IP_or_FQDN>/docs/api/
```

The Swagger UI provides:
- Code samples
- "Try it out" browser experience
- Input/output parameter details
- Live testing capabilities

### OpenAPI Specification
The OpenAPI (Swagger) specification is not available for public download but can be retrieved from your Unified Manager instance:
1. Access the Swagger UI
2. Use browser developer tools to capture the `/swagger.json` or `/openapi.json` request
3. Save the JSON content for local use

## Development Support

### Client Libraries
Any REST client or programming language can interact with the API:
- Python
- Perl
- Java
- cURL
- Any HTTP client library

### Automation Integration
The APIs are designed for integration into automation workflows, enabling:
- Scripted health checks
- Automated risk detection
- Scheduled data extraction
- Workflow automation

## Common Parameters

The API supports several common query parameters:

- `fields`: Specify which fields to return
- `max_records`: Limit the number of records returned
- `offset`: Start index for pagination
- `order_by`: Sort results by specified field
- `query`: Search using 'contains' relationship
- `return_records`: Control whether to return record data or just counts

## Data Models

The API defines numerous data models for different resources including:
- Access endpoints (with IP, gateway, VLAN configurations)
- Performance metrics (with accumulative statistics)
- Storage metrics
- Cluster information
- SVM (Storage Virtual Machine) details
- Performance service levels
- Workload management

## Next Steps

- [API Endpoints Reference](./api-endpoints.md) - Detailed list of available endpoints
- [Data Models](./data-models.md) - Complete data model documentation
- [Examples](./examples.md) - Code examples and use cases

## Resources

- [Official NetApp ActiveIQ Documentation](https://docs.netapp.com/us-en/active-iq/)
- [Active IQ Unified Manager API Automation Guide](https://docs.netapp.com/us-en/active-iq-unified-manager/api-automation/concept_get_started_with_um_apis.html)
- [Digital Advisor API Services](https://docs.netapp.com/us-en/active-iq/concept_overview_API_service.html)
