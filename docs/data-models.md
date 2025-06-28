# NetApp ActiveIQ API - Data Models

This document describes the key data models and schemas used in the NetApp ActiveIQ Unified Manager REST API.

## Overview

The API uses JSON for all request and response payloads. All data models are based on OpenAPI 2.0 specification and include detailed property descriptions, data types, and constraints.

## Common Properties

Many objects in the API share common structural elements:

### Links Object (`_links`)
```json
{
  "_links": {
    "self": {
      "href": "string"
    },
    "next": {
      "href": "string"
    }
  }
}
```
- **self**: Link to the current resource
- **next**: Link to the next page (for paginated responses)

### Response Wrapper
Most collection responses follow this pattern:
```json
{
  "_links": {},
  "num_records": 0,
  "records": [],
  "total_records": 0
}
```

## Core Data Models

### 1. Access Endpoint

Represents network access points for storage resources.

```json
{
  "_links": {},
  "data_protocols": ["nfs", "cifs", "iscsi", "fcp"],
  "fileshare": {
    "key": "string"
  },
  "gateway": "10.132.72.12",
  "gateways": ["10.142.56.12"],
  "ip": {
    "address": "10.162.83.26",
    "ha_address": "10.142.83.26",
    "netmask": "255.255.0.0"
  },
  "key": "string",
  "lun": {
    "key": "string"
  },
  "mtu": 15000,
  "name": "aep1",
  "svm": {
    "_links": {},
    "key": "string",
    "name": "svm1",
    "uuid": "uuid"
  },
  "uuid": "uuid",
  "vlan": 10,
  "wwpn": "20:00:00:50:56:a7:bc:a2"
}
```

**Key Properties:**
- **data_protocols**: Supported protocols (NFS, CIFS, iSCSI, FCP)
- **ip**: Network configuration including address, netmask, and HA address
- **mtu**: Maximum Transmission Unit
- **vlan**: VLAN identifier
- **wwpn**: World Wide Port Name (for FCP)

### 2. Performance Metrics

#### Accumulative Metric
```json
{
  "other": {},
  "read": {},
  "total": {},
  "write": {}
}
```

#### Accumulative Submetric
```json
{
  "95th_percentile": 28.0,
  "avg": 28.0,
  "max": 28.0,
  "min": 28.0
}
```

**Performance Metrics Categories:**
- **read**: Read operation metrics
- **write**: Write operation metrics  
- **total**: Combined read/write metrics
- **other**: Other operation metrics

### 3. Cluster Information

```json
{
  "_links": {},
  "key": "string",
  "name": "fas8040-206-21",
  "uuid": "4c6bf721-2e3f-11e9-a3e2-00a0985badbb",
  "version": {
    "full": "NetApp Release Dayblazer__9.5.0: Thu Jan 17 10:28:33 UTC 2019"
  },
  "management_ip": "10.226.207.25",
  "nodes": [
    {
      "uuid": "12cf06cc-2e3a-11e9-b9b4-00a0985badbb",
      "name": "fas8040-206-21-01",
      "model": "FAS8040"
    }
  ]
}
```

### 4. Storage Virtual Machine (SVM)

```json
{
  "_links": {},
  "key": "string",
  "name": "svm1",
  "uuid": "1d1c3198-fc57-11a8-99ca-00a078d39e12"
}
```

### 5. Storage Metrics

#### Space Usage
```json
{
  "size": {
    "available": 1073741824,
    "total": 2147483648,
    "used": 1073741824
  }
}
```

#### Efficiency Metrics
```json
{
  "efficiency": {
    "compression": {
      "savings": 1073741824,
      "ratio": "2:1"
    },
    "deduplication": {
      "savings": 536870912,
      "ratio": "1.5:1"
    }
  }
}
```

### 6. Event Management

#### Event Object
```json
{
  "_links": {},
  "key": "string",
  "name": "Event Name",
  "message": "Event description",
  "severity": "critical",
  "state": "new",
  "acknowledged": false,
  "resolved": false,
  "source": {
    "key": "string",
    "name": "Source Object"
  },
  "time": "2023-01-01T12:00:00Z"
}
```

**Event Severities:**
- `critical`
- `warning` 
- `information`
- `error`

**Event States:**
- `new`
- `acknowledged`
- `resolved`
- `obsolete`

### 7. Job Management

#### Job Object
```json
{
  "_links": {},
  "uuid": "string",
  "description": "Job description",
  "state": "success",
  "start_time": "2023-01-01T12:00:00Z",
  "end_time": "2023-01-01T12:05:00Z",
  "progress": 100,
  "message": "Job completed successfully"
}
```

**Job States:**
- `queued`
- `running`
- `paused`
- `success`
- `failure`
- `partial_failures`

### 8. Performance Service Level

```json
{
  "_links": {},
  "key": "string",
  "name": "Extreme",
  "description": "High performance service level",
  "expected_iops": {
    "allocation": "allocated_space",
    "peak": 10000,
    "per_tb": 1000
  },
  "peak_iops": {
    "allocation": "allocated_space", 
    "absolute": 50000,
    "per_tb": 5000
  },
  "expected_latency": 1,
  "peak_latency": 2,
  "block_size": "any"
}
```

### 9. Backup Information

#### Backup Settings
```json
{
  "enabled": true,
  "frequency": "daily",
  "hour": 1,
  "minute": 17,
  "day_of_week": null,
  "retention_count": 10,
  "path": "/opt/netapp/data/ocum-backup/"
}
```

#### Backup File Info
```json
{
  "name": "backup_20230101_120000.sql",
  "path": "/opt/netapp/data/ocum-backup/backup_20230101_120000.sql",
  "size": 1073741824,
  "creation_time": "2023-01-01T12:00:00Z",
  "type": "mysql"
}
```

## Common Data Types

### Primitive Types
- **string**: Text values
- **integer**: Whole numbers
- **number/double**: Decimal numbers  
- **boolean**: true/false values
- **uuid**: UUID format strings
- **int64**: 64-bit integers

### Date/Time Format
All timestamps use ISO 8601 format:
```
YYYY-MM-DDTHH:mm:ssZ
```

### Enumerated Values
Many fields use predefined enumerated values for consistency:

**Protocols:**
- `nfs`
- `cifs` 
- `iscsi`
- `fcp`

**Frequencies:**
- `daily`
- `weekly`

**Allocation Types:**
- `allocated_space`
- `used_space`

## Error Response Format

All error responses follow this structure:
```json
{
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE",
    "target": "field_name"
  }
}
```

## Pagination

Collection responses include pagination metadata:
```json
{
  "num_records": 20,
  "total_records": 150,
  "_links": {
    "self": {"href": "/api/v2/endpoint?offset=0&max_records=20"},
    "next": {"href": "/api/v2/endpoint?offset=20&max_records=20"}
  }
}
```

## Field Selection

Use the `fields` parameter to specify which properties to include in responses:
```
GET /api/v2/datacenter/cluster/clusters?fields=name,uuid,version
```

This returns only the specified fields, reducing response size and improving performance.

For complete schema definitions and additional models, refer to the OpenAPI specification available through your Unified Manager Swagger interface.
