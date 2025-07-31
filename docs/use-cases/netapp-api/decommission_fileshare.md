# Use Case: Decommissioning a File Share

This sequence diagram shows the process of authenticating, finding a file share, and then deleting it.

```mermaid
sequenceDiagram
    participant AS as Automation Script
    participant API as NetApp ActiveIQ API

    AS->>+API: Authenticate (HTTP Basic Auth)
    API-->>-AS: 200 OK (Authentication Successful)

    Note over AS, API: All subsequent requests are authenticated

    AS->>+API: GET /storage-provider/file-shares (Find File Share)
    API-->>-AS: 200 OK (List of File Shares)

    AS->>+API: DELETE /storage-provider/file-shares/{key} (Delete File Share)
    API-->>-AS: 202 Accepted (Job Key)

    loop Poll Job Status
        AS->>+API: GET /management-server/jobs/{job_key}
        API-->>-AS: 200 OK (Job Status)
    end
```

## Inputs

### Authentication

- **Username**: NetApp ActiveIQ API username with file share management privileges
- **Password**: Corresponding password for API authentication
- **Base URL**: NetApp ActiveIQ Unified Manager base URL (e.g., `https://aiq-um.example.com`)

### File Share Identification

- **File Share Key**: Unique key for the file share (e.g., CIFS share name, export path, or internal UUID)
- **File Share Name**: Human-readable name or path for the file share (alternative to key)
- **SVM Context**: Storage Virtual Machine where the file share resides

### Search/Filter Parameters (for GET /storage-provider/file-shares)

- **name**: Filter file shares by name or path
- **svm.name**: Filter by SVM name
- **max_records**: Maximum number of records to return (default: 20)
- **order_by**: Sort results by specified field (e.g., `name`, `creation_time`, `usage`)

### Decommission Parameters

- **Force Delete**: Indicates whether to force file share deletion if in use
  - **Type**: Boolean
  - **Default**: false
- **Delete Reason**: Optional metadata for deletion audit trail
  - **Type**: String
  - **Examples**:
    - `"End of Project Lifecycle"`
    - `"Security Risks Identified"`
    - `"Migrated to New SVM"`

### DELETE Request Configuration

- **URL Format**: `DELETE /storage-provider/file-shares/{key}`
- **Headers**: Include `Authorization` and `Content-Type: application/json`
- **Force or Safe**: Apply force delete only when absolutely necessary

### Pre-Delete Checks

- **Active Connections**: Verify no active connections before deletion (unless forced)
- **User Notifications**: Inform users of pending decommission
- **Audit Requirements**: Ensure audit compliance and record deletion reason

### Error Handling

- **Authentication Failure (401 Unauthorized)**: If authentication fails, the script should log the error and terminate. Ensure that the API credentials are correct and have the necessary permissions.
- **File Share Not Found (404 Not Found)**: If the file share to be deleted is not found, the script should handle the error appropriately. This could mean the file share has already been deleted, which may be acceptable depending on the use case.
- **Forbidden (403 Forbidden)**: If the user doesn't have permissions to delete the file share, the script should log the error and notify the administrator.
- **File Share In Use (400 Bad Request)**: If the file share is currently in use (e.g., has active connections), the API may return a 400 error. The script should handle this by either forcing the deletion (if appropriate) or notifying the user to disconnect clients first.
- **Job Failure**: The deletion job may fail for various reasons (e.g., dependencies, system constraints). The script should monitor the job status and provide detailed error information if the job fails.
- **Network Errors**: Implement retry logic with exponential backoff for transient network errors.
