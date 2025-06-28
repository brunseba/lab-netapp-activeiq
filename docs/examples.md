# NetApp ActiveIQ API - Examples and Use Cases

This document provides practical examples and common use cases for the NetApp ActiveIQ Unified Manager REST API.

## Prerequisites

- NetApp Active IQ Unified Manager instance running
- Valid credentials with appropriate roles (Operator, Storage Administrator, or Application Administrator)
- Basic understanding of REST API concepts

## Authentication

All examples use HTTP Basic Authentication. Replace `<username>`, `<password>`, and `<um-host>` with your actual values.

```bash
# Using curl
curl -u "<username>:<password>" -X GET "https://<um-host>/api/v2/datacenter/cluster/clusters"

# Using Python requests
import requests
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('<username>', '<password>')
response = requests.get('https://<um-host>/api/v2/datacenter/cluster/clusters', auth=auth)
```

## Common Use Cases

### 1. Infrastructure Discovery

#### Get All Clusters
```bash
# Basic cluster information
curl -u "admin:password" -X GET \
  "https://um-server.example.com/api/v2/datacenter/cluster/clusters"

# Get specific fields only
curl -u "admin:password" -X GET \
  "https://um-server.example.com/api/v2/datacenter/cluster/clusters?fields=name,uuid,version,management_ip"
```

**Python Example:**
```python
import requests
from requests.auth import HTTPBasicAuth

def get_clusters(um_host, username, password):
    url = f"https://{um_host}/api/v2/datacenter/cluster/clusters"
    params = {"fields": "name,uuid,version,management_ip"}
    
    response = requests.get(url, auth=HTTPBasicAuth(username, password), params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

clusters = get_clusters("um-server.example.com", "admin", "password")
for cluster in clusters.get('records', []):
    print(f"Cluster: {cluster['name']} - Version: {cluster['version']['full']}")
```

#### Get All Storage Virtual Machines (SVMs)
```bash
curl -u "admin:password" -X GET \
  "https://um-server.example.com/api/v2/datacenter/svm/svms?fields=name,uuid,cluster"
```

### 2. Storage Monitoring

#### Get Volume Information
```bash
# Get all volumes with capacity information
curl -u "admin:password" -X GET \
  "https://um-server.example.com/api/v2/datacenter/storage/volumes?fields=name,size,svm,cluster"

# Get volumes with low available space (example query)
curl -u "admin:password" -X GET \
  "https://um-server.example.com/api/v2/datacenter/storage/volumes?query=size.available<1073741824"
```

**Python Example - Storage Capacity Report:**
```python
def generate_storage_report(um_host, username, password):
    url = f"https://{um_host}/api/v2/datacenter/storage/volumes"
    params = {
        "fields": "name,size,svm.name,cluster.name",
        "max_records": 100
    }
    
    response = requests.get(url, auth=HTTPBasicAuth(username, password), params=params)
    
    if response.status_code == 200:
        volumes = response.json()
        
        print("Storage Capacity Report")
        print("-" * 60)
        print(f"{'Volume':<20} {'Cluster':<15} {'SVM':<15} {'Size (GB)':<10} {'Available (GB)':<15}")
        print("-" * 60)
        
        for volume in volumes.get('records', []):
            size_gb = volume['size']['total'] / (1024**3)
            available_gb = volume['size']['available'] / (1024**3)
            
            print(f"{volume['name']:<20} {volume['cluster']['name']:<15} "
                  f"{volume['svm']['name']:<15} {size_gb:<10.2f} {available_gb:<15.2f}")
```

### 3. Performance Monitoring

#### Get Cluster Performance Metrics
```bash
curl -u "admin:password" -X GET \
  "https://um-server.example.com/api/v2/gateways/clusters/{cluster_uuid}/metrics/clusters/perf"
```

#### Get Volume Performance Data
```bash
curl -u "admin:password" -X GET \
  "https://um-server.example.com/api/v2/gateways/clusters/{cluster_uuid}/metrics/volumes/perf?duration=1h&interval=5m"
```

### 4. Event Management

#### Get All Critical Events
```bash
curl -u "admin:password" -X GET \
  "https://um-server.example.com/api/v2/management-server/events?query=severity:critical&fields=name,message,severity,state,time"
```

#### Acknowledge an Event
```bash
curl -u "admin:password" -X POST \
  "https://um-server.example.com/api/v2/management-server/events/{event_key}/acknowledge"
```

## Python Example - Event Dashboard

```python
def get_critical_events(um_host, username, password):
    url = f"https://{um_host}/api/v2/management-server/events"
    params = {
        "query": "severity:critical AND state:new",
        "fields": "name,message,severity,state,time,source",
        "order_by": "time desc",
        "max_records": 50
    }
    
    response = requests.get(url, auth=HTTPBasicAuth(username, password), params=params)
    
    if response.status_code == 200:
        events = response.json()
        
        print("Critical Events Dashboard")
        print("=" * 80)
        
        for event in events.get('records', []):
            print(f"Event: {event['name']}")
            print(f"Source: {event['source']['name']}")
            print(f"Time: {event['time']}")
            print(f"Message: {event['message']}")
            print("-" * 40)
    
    return events
```

### 5. Backup Management

#### Create a Backup
```bash
curl -u "admin:password" -X POST \
  "https://um-server.example.com/api/v2/admin/backup"
```

#### Get Backup Settings
```bash
curl -u "admin:password" -X GET \
  "https://um-server.example.com/api/v2/admin/backup-settings"
```

#### Update Backup Schedule
```bash
curl -u "admin:password" -X PATCH \
  "https://um-server.example.com/api/v2/admin/backup-settings" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "frequency": "daily",
    "hour": 2,
    "minute": 30,
    "retention_count": 7
  }'
```

### 6. Datasource Management

#### Add a New Cluster
```bash
curl -u "admin:password" -X POST \
  "https://um-server.example.com/api/v2/admin/datasources/clusters" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "10.226.207.154",
    "port": 443,
    "username": "admin",
    "password": "cluster_password",
    "protocol": "HTTPS"
  }'
```

#### Get Datasource Certificate
```bash
curl -u "admin:password" -X GET \
  "https://um-server.example.com/api/v2/admin/datasource-certificate?address=10.226.207.154&port=443"
```

### 7. Workload Management

#### Create a Performance Service Level
```bash
curl -u "admin:password" -X POST \
  "https://um-server.example.com/api/v2/storage-provider/performance-service-levels" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Performance SSD",
    "description": "High performance for critical workloads",
    "expected_iops": {
      "allocation": "allocated_space",
      "per_tb": 1000
    },
    "peak_iops": {
      "allocation": "allocated_space",
      "per_tb": 5000
    },
    "expected_latency": 1,
    "peak_latency": 2
  }'
```

#### Create a File Share
```bash
curl -u "admin:password" -X POST \
  "https://um-server.example.com/api/v2/storage-provider/file-shares" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "shared_data",
    "size": "100GB",
    "svm": {
      "key": "svm-key-here"
    },
    "performance_service_level": {
      "key": "psl-key-here"
    }
  }'
```

## Practical Automation Scripts

### Health Check Script
```python
#!/usr/bin/env python3
"""
NetApp UM Health Check Script
Checks cluster health, critical events, and storage capacity
"""

import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime

class NetAppHealthCheck:
    def __init__(self, um_host, username, password):
        self.um_host = um_host
        self.auth = HTTPBasicAuth(username, password)
        self.base_url = f"https://{um_host}/api/v2"
    
    def check_cluster_health(self):
        """Check overall cluster health"""
        url = f"{self.base_url}/datacenter/cluster/clusters"
        params = {"fields": "name,state,health"}
        
        response = requests.get(url, auth=self.auth, params=params)
        if response.status_code == 200:
            clusters = response.json()
            
            healthy_clusters = []
            unhealthy_clusters = []
            
            for cluster in clusters.get('records', []):
                if cluster.get('health', {}).get('overall_status') == 'healthy':
                    healthy_clusters.append(cluster['name'])
                else:
                    unhealthy_clusters.append(cluster['name'])
            
            return {
                'healthy': healthy_clusters,
                'unhealthy': unhealthy_clusters
            }
        return None
    
    def check_critical_events(self):
        """Get all unresolved critical events"""
        url = f"{self.base_url}/management-server/events"
        params = {
            "query": "severity:critical AND state:new",
            "fields": "name,source.name,time"
        }
        
        response = requests.get(url, auth=self.auth, params=params)
        if response.status_code == 200:
            return response.json().get('records', [])
        return []
    
    def check_storage_capacity(self, threshold_percent=90):
        """Check volumes approaching capacity threshold"""
        url = f"{self.base_url}/datacenter/storage/volumes"
        params = {"fields": "name,size,svm.name,cluster.name"}
        
        response = requests.get(url, auth=self.auth, params=params)
        if response.status_code == 200:
            volumes = response.json()
            high_capacity_volumes = []
            
            for volume in volumes.get('records', []):
                size = volume.get('size', {})
                if size.get('total', 0) > 0:
                    used_percent = (size.get('used', 0) / size.get('total', 1)) * 100
                    if used_percent > threshold_percent:
                        high_capacity_volumes.append({
                            'name': volume['name'],
                            'cluster': volume['cluster']['name'],
                            'svm': volume['svm']['name'],
                            'used_percent': round(used_percent, 2)
                        })
            
            return high_capacity_volumes
        return []
    
    def generate_report(self):
        """Generate comprehensive health report"""
        print("NetApp Unified Manager Health Check Report")
        print("=" * 60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Cluster Health
        cluster_health = self.check_cluster_health()
        if cluster_health:
            print("Cluster Health:")
            print(f"  Healthy: {len(cluster_health['healthy'])} clusters")
            print(f"  Unhealthy: {len(cluster_health['unhealthy'])} clusters")
            if cluster_health['unhealthy']:
                print(f"  Unhealthy clusters: {', '.join(cluster_health['unhealthy'])}")
            print()
        
        # Critical Events
        critical_events = self.check_critical_events()
        print(f"Critical Events: {len(critical_events)} unresolved")
        for event in critical_events[:5]:  # Show first 5
            print(f"  - {event['name']} on {event['source']['name']}")
        print()
        
        # Storage Capacity
        high_capacity = self.check_storage_capacity()
        print(f"High Capacity Volumes (>90%): {len(high_capacity)}")
        for volume in high_capacity[:5]:  # Show first 5
            print(f"  - {volume['name']} ({volume['used_percent']}%) on {volume['cluster']}")

# Usage
if __name__ == "__main__":
    health_check = NetAppHealthCheck("um-server.example.com", "admin", "password")
    health_check.generate_report()
```

## Error Handling Best Practices

```python
def make_api_request(url, auth, method='GET', data=None, retries=3):
    """Make API request with proper error handling and retries"""
    
    for attempt in range(retries):
        try:
            if method == 'GET':
                response = requests.get(url, auth=auth, timeout=30)
            elif method == 'POST':
                response = requests.post(url, auth=auth, json=data, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, auth=auth, json=data, timeout=30)
            
            # Handle different response codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print("Authentication failed - check credentials")
                return None
            elif response.status_code == 403:
                print("Access forbidden - check user permissions")
                return None
            elif response.status_code == 404:
                print("Resource not found")
                return None
            elif response.status_code >= 500:
                print(f"Server error: {response.status_code}")
                if attempt < retries - 1:
                    print(f"Retrying... (attempt {attempt + 2}/{retries})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                print(f"Unexpected status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"Request timeout (attempt {attempt + 1}/{retries})")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
        except requests.exceptions.ConnectionError:
            print(f"Connection error (attempt {attempt + 1}/{retries})")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
    
    print(f"Failed after {retries} attempts")
    return None
```

## Tips and Best Practices

1. **Use field selection** to reduce response size and improve performance
2. **Implement pagination** for large datasets using `max_records` and `offset`
3. **Handle rate limiting** with appropriate delays between requests
4. **Use HTTPS** for all communications
5. **Store credentials securely** - never hardcode passwords
6. **Validate SSL certificates** in production environments
7. **Implement proper error handling** and retry logic
8. **Log API interactions** for debugging and audit purposes

For more examples and detailed parameter information, refer to the interactive Swagger documentation at:
```
https://<your-unified-manager>/apidocs/
```
