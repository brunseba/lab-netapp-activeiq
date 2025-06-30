# NetApp ActiveIQ API - Endpoints Reference

This document provides a comprehensive list of available API endpoints in the NetApp ActiveIQ Unified Manager REST API.

## Base URL Structure
```
https://<hostname>:<port>/api/v2
```

## Endpoint Categories

### 1. Administration (`/admin/*`)

#### Backup Management
- **POST** `/admin/backup` - Create a backup request
- **GET** `/admin/backup-file-info` - Retrieve information on all backup files
- **GET** `/admin/backup-settings` - Get scheduled backup settings
- **PATCH** `/admin/backup-settings` - Update scheduled backup settings

#### Datasource Management
- **GET** `/admin/datasource-certificate` - Retrieve datasource certificate details
- **GET** `/admin/datasources/clusters` - Get all datasources
- **POST** `/admin/datasources/clusters` - Add a new datasource
- **DELETE** `/admin/datasources/clusters/{key}` - Remove a datasource
- **GET** `/admin/datasources/clusters/{key}` - Get specific datasource details
- **PATCH** `/admin/datasources/clusters/{key}` - Update datasource configuration

### 2. Datacenter (`/datacenter/*`)

#### Cluster Management
- **GET** `/datacenter/cluster/clusters` - Get cluster information
- **GET** `/datacenter/cluster/clusters/{key}` - Get specific cluster details
- **GET** `/datacenter/cluster/clusters/{key}/nodes` - Get cluster nodes
- **GET** `/datacenter/cluster/clusters/{key}/nodes/{uuid}` - Get specific node details

#### Storage Virtual Machines (SVMs)
- **GET** `/datacenter/svm/svms` - Get all SVMs
- **GET** `/datacenter/svm/svms/{key}` - Get specific SVM details

#### Storage Management
- **GET** `/datacenter/storage/aggregates` - Get storage aggregates
- **GET** `/datacenter/storage/aggregates/{key}` - Get specific aggregate details
- **GET** `/datacenter/storage/disks` - Get disk information
- **GET** `/datacenter/storage/disks/{key}` - Get specific disk details
- **GET** `/datacenter/storage/volumes` - Get volume information
- **GET** `/datacenter/storage/volumes/{key}` - Get specific volume details
- **GET** `/datacenter/storage/luns` - Get LUN information
- **GET** `/datacenter/storage/luns/{key}` - Get specific LUN details
- **GET** `/datacenter/storage/qtrees` - Get qtree information
- **GET** `/datacenter/storage/qtrees/{key}` - Get specific qtree details

#### Access Endpoints
- **GET** `/datacenter/svm/svms/{svm.key}/access-endpoints` - Get SVM access endpoints
- **POST** `/datacenter/svm/svms/{svm.key}/access-endpoints` - Create SVM access endpoint
- **DELETE** `/datacenter/svm/svms/{svm.key}/access-endpoints/{uuid}` - Delete access endpoint
- **GET** `/datacenter/svm/svms/{svm.key}/access-endpoints/{uuid}` - Get specific access endpoint
- **PATCH** `/datacenter/svm/svms/{svm.key}/access-endpoints/{uuid}` - Update access endpoint

### 3. Storage Provider (`/storage-provider/*`)

#### Performance Service Levels
- **GET** `/storage-provider/performance-service-levels` - Get performance service levels
- **POST** `/storage-provider/performance-service-levels` - Create performance service level
- **DELETE** `/storage-provider/performance-service-levels/{key}` - Delete performance service level
- **GET** `/storage-provider/performance-service-levels/{key}` - Get specific performance service level
- **PATCH** `/storage-provider/performance-service-levels/{key}` - Update performance service level

#### File Shares
- **GET** `/storage-provider/file-shares` - Get file shares
- **POST** `/storage-provider/file-shares` - Create file share
- **DELETE** `/storage-provider/file-shares/{key}` - Delete file share
- **GET** `/storage-provider/file-shares/{key}` - Get specific file share
- **PATCH** `/storage-provider/file-shares/{key}` - Update file share

#### LUNs
- **GET** `/storage-provider/luns` - Get LUNs
- **POST** `/storage-provider/luns` - Create LUN
- **DELETE** `/storage-provider/luns/{key}` - Delete LUN
- **GET** `/storage-provider/luns/{key}` - Get specific LUN
- **PATCH** `/storage-provider/luns/{key}` - Update LUN

### 4. Management Server (`/management-server/*`)

#### Events and Alerts
- **GET** `/management-server/events` - Get events
- **POST** `/management-server/events/{key}/acknowledge` - Acknowledge event
- **DELETE** `/management-server/events/{key}/acknowledge` - Un-acknowledge event
- **POST** `/management-server/events/{key}/assign-to` - Assign event to user
- **POST** `/management-server/events/{key}/resolve` - Resolve event

#### Jobs
- **GET** `/management-server/jobs` - Get jobs
- **GET** `/management-server/jobs/{uuid}` - Get specific job details

#### System Information
- **GET** `/management-server/system` - Get system information
- **GET** `/management-server/version` - Get version information

### 5. Gateways (`/gateways/*`)

#### Gateway APIs
- **GET** `/gateways/clusters/{cluster_uuid}/events` - Get cluster events via gateway
- **GET** `/gateways/clusters/{cluster_uuid}/metrics/aggregates/perf` - Get aggregate performance metrics
- **GET** `/gateways/clusters/{cluster_uuid}/metrics/clusters/perf` - Get cluster performance metrics
- **GET** `/gateways/clusters/{cluster_uuid}/metrics/volumes/perf` - Get volume performance metrics

## Common Query Parameters

All GET endpoints support these common query parameters:

- **fields** (array): Specify which fields to return
- **max_records** (integer): Limit the number of records returned (default: 20)
- **offset** (integer): Start index for pagination (default: 0)
- **order_by** (string): Sort results by field [asc|desc] (default: asc)
- **query** (string): Search using 'contains' relationship
- **return_records** (boolean): Control whether to return record data or just counts

## HTTP Methods and Response Codes

### Supported HTTP Methods
- **GET**: Retrieve resources
- **POST**: Create new resources
- **PATCH**: Update existing resources
- **DELETE**: Remove resources

### Common Response Codes
- **200**: OK - Request successful
- **201**: Created - Resource created successfully
- **202**: Accepted - Request accepted for processing
- **400**: Bad Request - Invalid request parameters
- **401**: Unauthorized - Authentication required
- **403**: Forbidden - Access denied
- **404**: Not Found - Resource not found
- **500**: Internal Server Error - Server error

## Authentication

All endpoints require HTTP Basic Authentication with one of these roles:
- Operator
- Storage Administrator
- Application Administrator

## Content Type

All requests and responses use:
```
Content-Type: application/json
```

## Example Usage

### Get All Clusters
```bash
GET /api/v2/datacenter/cluster/clusters
```

### Get Cluster with Specific Fields
```bash
GET /api/v2/datacenter/cluster/clusters?fields=name,uuid,version
```

### Create a Backup
```bash
POST /api/v2/admin/backup
Content-Type: application/json
```

### Get Events with Pagination
```bash
GET /api/v2/management-server/events?max_records=50&offset=100
```

For detailed parameter information and examples for each endpoint, refer to the interactive Swagger documentation available at:
```
https://<your-unified-manager>/apidocs/
```
