# NetApp ActiveIQ API - Use Cases Reference Table

This document provides a comprehensive table of NetApp ActiveIQ API endpoints organized by use cases and scenarios.

## Table of Contents
1. [Infrastructure Discovery & Monitoring](#infrastructure-discovery--monitoring)
2. [Storage Management & Provisioning](#storage-management--provisioning)
3. [Performance Monitoring & Analytics](#performance-monitoring--analytics)
4. [Event & Alert Management](#event--alert-management)
5. [Backup & Administration](#backup--administration)
6. [Security & Access Management](#security--access-management)
7. [Workload & Service Level Management](#workload--service-level-management)
8. [Automation & Integration](#automation--integration)

---

## Infrastructure Discovery & Monitoring

| **Use Case** | **API Endpoint** | **HTTP Method** | **Description** | **Common Parameters** | **Example Scenario** |
|--------------|------------------|-----------------|-----------------|----------------------|---------------------|
| **Cluster Discovery** | `/datacenter/cluster/clusters` | GET | Get all cluster information | `fields=name,uuid,version,management_ip` | Initial environment discovery, inventory management |
| **Cluster Details** | `/datacenter/cluster/clusters/{key}` | GET | Get specific cluster details | `fields=name,state,health,version` | Health checks, cluster validation |
| **Node Information** | `/datacenter/cluster/clusters/{key}/nodes` | GET | Get cluster nodes | `fields=name,uuid,model,serial_number` | Hardware inventory, capacity planning |
| **Node Details** | `/datacenter/cluster/clusters/{key}/nodes/{uuid}` | GET | Get specific node details | `fields=name,model,uptime,health` | Node-specific monitoring, troubleshooting |
| **SVM Discovery** | `/datacenter/svm/svms` | GET | Get all Storage Virtual Machines | `fields=name,uuid,cluster,state` | Multi-tenant environment mapping |
| **SVM Details** | `/datacenter/svm/svms/{key}` | GET | Get specific SVM details | `fields=name,state,protocols,dns` | SVM configuration validation |
| **System Information** | `/management-server/system` | GET | Get system information | N/A | Environment documentation, compliance |
| **Version Information** | `/management-server/version` | GET | Get version information | N/A | Version tracking, upgrade planning |

---

## Storage Management & Provisioning

| **Use Case** | **API Endpoint** | **HTTP Method** | **Description** | **Common Parameters** | **Example Scenario** |
|--------------|------------------|-----------------|-----------------|----------------------|---------------------|
| **Volume Management** | `/datacenter/storage/volumes` | GET | Get all volumes | `fields=name,size,svm,cluster` | Capacity reporting, storage inventory |
| **Volume Details** | `/datacenter/storage/volumes/{key}` | GET | Get specific volume details | `fields=name,size,space,snapshot_policy` | Volume analysis, capacity planning |
| **Aggregate Management** | `/datacenter/storage/aggregates` | GET | Get storage aggregates | `fields=name,space,state,raid_type` | Storage pool management |
| **Aggregate Details** | `/datacenter/storage/aggregates/{key}` | GET | Get specific aggregate details | `fields=space.size,space.available,state` | Capacity monitoring, performance analysis |
| **LUN Management** | `/datacenter/storage/luns` | GET | Get LUN information | `fields=name,size,os_type,serial_number` | SAN storage management |
| **LUN Details** | `/datacenter/storage/luns/{key}` | GET | Get specific LUN details | `fields=name,size,space,serial_number` | LUN monitoring, space management |
| **Qtree Management** | `/datacenter/storage/qtrees` | GET | Get qtree information | `fields=name,volume,svm,quota` | File system organization |
| **Qtree Details** | `/datacenter/storage/qtrees/{key}` | GET | Get specific qtree details | `fields=name,path,security_style` | Qtree configuration validation |
| **Disk Information** | `/datacenter/storage/disks` | GET | Get disk information | `fields=name,type,size,container` | Hardware inventory, disk utilization |
| **Disk Details** | `/datacenter/storage/disks/{key}` | GET | Get specific disk details | `fields=name,state,type,rpm` | Disk health monitoring |
| **File Share Creation** | `/storage-provider/file-shares` | POST | Create file share | N/A | NFS/CIFS share provisioning |
| **File Share Management** | `/storage-provider/file-shares` | GET | Get file shares | `fields=name,size,svm,export_policy` | Share inventory, access management |
| **File Share Details** | `/storage-provider/file-shares/{key}` | GET | Get specific file share | `fields=name,path,protocols,access` | Share configuration review |
| **File Share Updates** | `/storage-provider/file-shares/{key}` | PATCH | Update file share | N/A | Share modification, policy updates |
| **File Share Deletion** | `/storage-provider/file-shares/{key}` | DELETE | Delete file share | N/A | Share cleanup, decommissioning |
| **LUN Provisioning** | `/storage-provider/luns` | POST | Create LUN | N/A | SAN storage provisioning |
| **LUN Management** | `/storage-provider/luns` | GET | Get LUNs | `fields=name,size,os_type,location` | SAN storage inventory |
| **LUN Updates** | `/storage-provider/luns/{key}` | PATCH | Update LUN | N/A | LUN modification, size changes |
| **LUN Deletion** | `/storage-provider/luns/{key}` | DELETE | Delete LUN | N/A | LUN cleanup, storage reclamation |

---

## Performance Monitoring & Analytics

| **Use Case** | **API Endpoint** | **HTTP Method** | **Description** | **Common Parameters** | **Example Scenario** |
|--------------|------------------|-----------------|-----------------|----------------------|---------------------|
| **Cluster Performance** | `/gateways/clusters/{cluster_uuid}/metrics/clusters/perf` | GET | Get cluster performance metrics | `duration=1h&interval=5m` | Performance monitoring, trend analysis |
| **Volume Performance** | `/gateways/clusters/{cluster_uuid}/metrics/volumes/perf` | GET | Get volume performance data | `duration=24h&interval=1h` | Volume performance analysis |
| **Aggregate Performance** | `/gateways/clusters/{cluster_uuid}/metrics/aggregates/perf` | GET | Get aggregate performance metrics | `duration=1d&interval=5m` | Storage pool performance monitoring |
| **Cluster Events** | `/gateways/clusters/{cluster_uuid}/events` | GET | Get cluster events via gateway | `severity=critical&max_records=100` | Performance issue correlation |

---

## Event & Alert Management

| **Use Case** | **API Endpoint** | **HTTP Method** | **Description** | **Common Parameters** | **Example Scenario** |
|--------------|------------------|-----------------|-----------------|----------------------|---------------------|
| **Event Monitoring** | `/management-server/events` | GET | Get all events | `query=severity:critical&fields=name,message,time` | Critical event monitoring |
| **Event Acknowledgment** | `/management-server/events/{key}/acknowledge` | POST | Acknowledge event | N/A | Event management workflow |
| **Event Un-acknowledgment** | `/management-server/events/{key}/acknowledge` | DELETE | Un-acknowledge event | N/A | Event management correction |
| **Event Assignment** | `/management-server/events/{key}/assign-to` | POST | Assign event to user | N/A | Incident management workflow |
| **Event Resolution** | `/management-server/events/{key}/resolve` | POST | Resolve event | N/A | Incident closure, problem resolution |

---

## Backup & Administration

| **Use Case** | **API Endpoint** | **HTTP Method** | **Description** | **Common Parameters** | **Example Scenario** |
|--------------|------------------|-----------------|-----------------|----------------------|---------------------|
| **Backup Creation** | `/admin/backup` | POST | Create a backup request | N/A | Scheduled backup automation |
| **Backup Information** | `/admin/backup-file-info` | GET | Get backup file information | N/A | Backup inventory, space management |
| **Backup Settings** | `/admin/backup-settings` | GET | Get scheduled backup settings | N/A | Backup configuration review |
| **Backup Configuration** | `/admin/backup-settings` | PATCH | Update backup settings | N/A | Backup policy management |
| **Job Monitoring** | `/management-server/jobs` | GET | Get all jobs | `fields=state,progress,message` | Operation monitoring |
| **Job Details** | `/management-server/jobs/{uuid}` | GET | Get specific job details | `fields=state,start_time,end_time` | Job tracking, troubleshooting |

---

## Security & Access Management

| **Use Case** | **API Endpoint** | **HTTP Method** | **Description** | **Common Parameters** | **Example Scenario** |
|--------------|------------------|-----------------|-----------------|----------------------|---------------------|
| **Datasource Certificate** | `/admin/datasource-certificate` | GET | Get datasource certificate details | `address=cluster_ip&port=443` | SSL certificate validation |
| **Datasource Management** | `/admin/datasources/clusters` | GET | Get all datasources | `fields=address,port,protocol` | Cluster connection inventory |
| **Datasource Addition** | `/admin/datasources/clusters` | POST | Add new datasource | N/A | Cluster onboarding automation |
| **Datasource Removal** | `/admin/datasources/clusters/{key}` | DELETE | Remove datasource | N/A | Cluster decommissioning |
| **Datasource Details** | `/admin/datasources/clusters/{key}` | GET | Get specific datasource details | `fields=address,state,last_update` | Connection status monitoring |
| **Datasource Updates** | `/admin/datasources/clusters/{key}` | PATCH | Update datasource configuration | N/A | Credential updates, configuration changes |
| **Access Endpoints** | `/datacenter/svm/svms/{svm.key}/access-endpoints` | GET | Get SVM access endpoints | `fields=ip,gateway,vlan` | Network access management |
| **Access Endpoint Creation** | `/datacenter/svm/svms/{svm.key}/access-endpoints` | POST | Create SVM access endpoint | N/A | Network provisioning |
| **Access Endpoint Deletion** | `/datacenter/svm/svms/{svm.key}/access-endpoints/{uuid}` | DELETE | Delete access endpoint | N/A | Network cleanup |
| **Access Endpoint Details** | `/datacenter/svm/svms/{svm.key}/access-endpoints/{uuid}` | GET | Get specific access endpoint | `fields=ip,protocols,services` | Network configuration review |
| **Access Endpoint Updates** | `/datacenter/svm/svms/{svm.key}/access-endpoints/{uuid}` | PATCH | Update access endpoint | N/A | Network reconfiguration |

---

## Workload & Service Level Management

| **Use Case** | **API Endpoint** | **HTTP Method** | **Description** | **Common Parameters** | **Example Scenario** |
|--------------|------------------|-----------------|-----------------|----------------------|---------------------|
| **Performance Service Levels** | `/storage-provider/performance-service-levels` | GET | Get performance service levels | `fields=name,expected_iops,peak_iops` | Service level inventory |
| **PSL Creation** | `/storage-provider/performance-service-levels` | POST | Create performance service level | N/A | Custom service level definition |
| **PSL Deletion** | `/storage-provider/performance-service-levels/{key}` | DELETE | Delete performance service level | N/A | Service level cleanup |
| **PSL Details** | `/storage-provider/performance-service-levels/{key}` | GET | Get specific performance service level | `fields=name,iops,latency,allocation` | Service level configuration review |
| **PSL Updates** | `/storage-provider/performance-service-levels/{key}` | PATCH | Update performance service level | N/A | Service level modification |

---

## Automation & Integration

| **Use Case** | **API Endpoint** | **HTTP Method** | **Description** | **Common Parameters** | **Example Scenario** |
|--------------|------------------|-----------------|-----------------|----------------------|---------------------|
| **Health Check Automation** | Multiple endpoints | GET | Automated health checks | `fields=health,state,status` | Automated monitoring scripts |
| **Capacity Reporting** | Volume/Aggregate endpoints | GET | Automated capacity reporting | `fields=size,available,used_percent` | Capacity management automation |
| **Event Dashboard** | `/management-server/events` | GET | Automated event monitoring | `query=state:new&severity=critical` | Dashboard integration |
| **Backup Automation** | `/admin/backup*` | GET/POST/PATCH | Automated backup management | N/A | Backup workflow automation |
| **Provisioning Automation** | Storage Provider endpoints | POST/PATCH | Automated resource provisioning | N/A | Self-service portals |
| **Compliance Reporting** | Multiple endpoints | GET | Automated compliance checks | Various field selections | Regulatory compliance automation |

---

## Use Case Categories Summary

### **Monitoring & Observability**
- **Infrastructure Discovery**: Cluster, node, and SVM discovery
- **Performance Monitoring**: Real-time and historical performance data
- **Event Management**: Critical event monitoring and alerting
- **Health Checks**: Automated health status validation

### **Storage Operations**
- **Provisioning**: Volume, LUN, and file share creation
- **Management**: Storage resource lifecycle management
- **Capacity Planning**: Space utilization and growth tracking
- **Performance Analysis**: Storage performance optimization

### **Administration & Security**
- **Backup Management**: Automated backup operations
- **Access Control**: Network and security configuration
- **Certificate Management**: SSL certificate validation
- **User Management**: Role-based access control

### **Integration & Automation**
- **Workflow Automation**: End-to-end process automation
- **Custom Dashboards**: Integration with monitoring systems
- **Self-Service Portals**: User-driven resource provisioning
- **Compliance**: Automated compliance and audit reporting

---

## Common Query Parameters Reference

| **Parameter** | **Type** | **Description** | **Example Usage** |
|---------------|----------|-----------------|-------------------|
| `fields` | Array | Specify which fields to return | `fields=name,uuid,state` |
| `max_records` | Integer | Limit number of records (default: 20) | `max_records=100` |
| `offset` | Integer | Start index for pagination (default: 0) | `offset=50` |
| `order_by` | String | Sort results by field [asc\|desc] | `order_by=name desc` |
| `query` | String | Search using 'contains' relationship | `query=severity:critical` |
| `return_records` | Boolean | Return record data or just counts | `return_records=false` |

---

## HTTP Response Codes

| **Code** | **Status** | **Description** | **Use Case** |
|----------|------------|-----------------|--------------|
| 200 | OK | Request successful | Successful GET operations |
| 201 | Created | Resource created successfully | Successful POST operations |
| 202 | Accepted | Request accepted for processing | Asynchronous operations |
| 400 | Bad Request | Invalid request parameters | Parameter validation errors |
| 401 | Unauthorized | Authentication required | Credential issues |
| 403 | Forbidden | Access denied | Permission issues |
| 404 | Not Found | Resource not found | Invalid resource keys |
| 500 | Internal Server Error | Server error | System issues |

---

## Authentication Requirements

All API endpoints require HTTP Basic Authentication with one of these roles:
- **Operator**: Read-only access to most resources
- **Storage Administrator**: Read/write access to storage resources
- **Application Administrator**: Full administrative access

**Content-Type**: All requests and responses use `application/json`

---

## Best Practices for API Usage

1. **Use field selection** to reduce response size and improve performance
2. **Implement pagination** for large datasets using `max_records` and `offset`
3. **Handle rate limiting** with appropriate delays between requests
4. **Use HTTPS** for all communications
5. **Store credentials securely** - never hardcode passwords
6. **Implement proper error handling** and retry logic
7. **Monitor API usage** for performance optimization
8. **Use specific fields** rather than returning all data

---

*For detailed examples and implementation guidance, refer to the [Examples](./examples.md) and [Advanced Use Cases](./advanced-use-cases.md) documentation.*
