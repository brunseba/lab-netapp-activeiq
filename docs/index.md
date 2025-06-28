---
tags:
  - NetApp
  - ActiveIQ
  - API
  - REST
  - Documentation
---

# NetApp ActiveIQ API Documentation

!!! info "Welcome to NetApp ActiveIQ API Documentation"
    Welcome to the comprehensive documentation for the NetApp ActiveIQ Unified Manager REST API. This documentation is based on analysis of external data sources and provides practical guidance for working with the API.

<div class="quick-ref-card">
<h3>🚀 Quick Start Guide</h3>
<p>Get started with NetApp ActiveIQ API in minutes</p>
</div>

## Overview

NetApp ActiveIQ provides a robust REST API suite through **Active IQ Unified Manager** and **Digital Advisor** to programmatically manage, monitor, and extract data from NetApp storage environments.

### Key Features
- **100+ API endpoints** across 20+ service categories
- **RESTful design** with full CRUD operations
- **JSON-based** request/response format
- **HTTP Basic Authentication**
- **Comprehensive coverage** of storage operations

## Documentation Structure

### 📖 [API Overview](./netapp-activeiq-api-overview.md)
General introduction to the NetApp ActiveIQ API, including:
- API capabilities and features
- Authentication and access requirements
- Getting started guide
- Common use cases

### 🔗 [API Endpoints Reference](./api-endpoints.md)
Complete reference of available API endpoints:
- Administration endpoints
- Datacenter management
- Storage provider operations
- Management server functions
- Gateway APIs

### 📊 [Data Models](./data-models.md)
Detailed documentation of API data structures:
- Core data models
- Performance metrics
- Event management objects
- Storage and cluster information
- Request/response formats

### 💻 [Examples and Use Cases](./examples.md)
Practical examples and automation scripts:
- Infrastructure discovery
- Storage monitoring
- Performance tracking
- Event management
- Backup automation
- Health check scripts

### 🚀 [Advanced Use Cases](./advanced-use-cases.md)
Advanced workflows with sequence diagrams:
- SVM creation automation
- NFS share management
- Credential updates and security
- Complete environment deployment
- Sequence diagrams for complex workflows
- Production-ready automation scripts

## Quick Start

### 1. Access Requirements
To use the ActiveIQ API, you need:
- Active IQ Unified Manager instance
- User account with appropriate role:
  - Operator
  - Storage Administrator
  - Application Administrator

### 2. Base URL
```
https://<your-unified-manager-host>/api/v2
```

### 3. Authentication
All API calls use HTTP Basic Authentication:
```bash
curl -u "username:password" -X GET "https://<host>/api/v2/datacenter/cluster/clusters"
```

### 4. Interactive Documentation
Access the Swagger UI for live API testing:
```
https://<your-unified-manager-host>/apidocs/
```

## Common Operations

### Get Cluster Information
```bash
GET /api/v2/datacenter/cluster/clusters
```

### Monitor Storage Capacity
```bash
GET /api/v2/datacenter/storage/volumes?fields=name,size,svm,cluster
```

### Check Critical Events
```bash
GET /api/v2/management-server/events?query=severity:critical
```

### Create Backup
```bash
POST /api/v2/admin/backup
```

## Data Sources

This documentation is derived from analysis of:
- NetApp ActiveIQ API research documents
- OpenAPI specification (16,674 lines)
- Official NetApp documentation references
- Practical implementation examples

## External Resources

- [Official NetApp ActiveIQ Documentation](https://docs.netapp.com/us-en/active-iq/)
- [Active IQ Unified Manager API Guide](https://docs.netapp.com/us-en/active-iq-unified-manager/api-automation/concept_get_started_with_um_apis.html)
- [Digital Advisor API Services](https://docs.netapp.com/us-en/active-iq/concept_overview_API_service.html)

---

*Last updated: Based on analysis of external data sources in donnees-externes/ folder*
