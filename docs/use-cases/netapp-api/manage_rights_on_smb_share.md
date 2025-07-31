# Use Case: Manage Rights on SMB Share

This use case describes how to manage access rights on an SMB/CIFS share using the NetApp API. It includes adding, modifying, and removing ACL (Access Control List) entries to control user and group permissions.

## Overview

Managing SMB share permissions enables administrators to control which users and groups have access to file shares and define their specific permissions (full control, read, write, etc.).

## API Endpoint

- **PATCH** `/api/storage/smb-shares/{share_id}/acl`
- **Permissions**: `storage-admin`

## Inputs

### Authentication

- **Username**: NetApp API username with SMB management privileges
- **Password**: Corresponding password for API authentication
- **Base URL**: NetApp Unified Manager URL (e.g., `https://netapp.example.com`)

### SMB Share Identification

- **Share ID**: Unique identifier of the SMB share
- **Share Name**: Human-readable name of the SMB share
- **SVM Context**: Storage Virtual Machine hosting the share

### ACL Configuration

- **User/Group**: Domain user or group to grant permissions to
- **Permission Level**: Type of access to grant
  - **Options**: `full-control`, `change`, `read`
- **Access Type**: Allow or deny access
  - **Options**: `allow`, `deny`

### Permission Examples

```json
{
  "acl_entries": [
    {
      "user_or_group": "DOMAIN\\username",
      "permission": "full-control",
      "access_type": "allow"
    },
    {
      "user_or_group": "DOMAIN\\groupname",
      "permission": "read",
      "access_type": "allow"
    }
  ]
}
```

### Input Validation Requirements

- User/group names must be valid in the domain
- Permission levels must be from supported options
- User must have SMB administration privileges
- Share must exist and be accessible

### Pre-Configuration Checks

- **Domain Integration**: Verify domain connectivity
- **User Validation**: Confirm users/groups exist in domain
- **Share Status**: Ensure SMB share is online and accessible

## Sequence Diagram

```mermaid
sequenceDiagram
    participant Admin as Administrator
    participant API as NetApp API
    participant SMB as SMB Service
    participant AD as Active Directory
    participant FS as File System

    Admin->>+API: Authenticate (Basic Auth)
    API-->>-Admin: 200 OK (Authentication Successful)

    Note over Admin, API: All subsequent requests are authenticated

    Admin->>+API: GET /storage/smb-shares (Find SMB Share)
    API-->>-Admin: 200 OK (List of SMB Shares)

    Admin->>+API: GET /storage/smb-shares/{share_id}/acl
    API-->>-Admin: 200 OK (Current ACL Entries)

    Admin->>+API: PATCH /storage/smb-shares/{share_id}/acl
    API->>+SMB: Process ACL Update Request

    loop For each user/group in ACL
        SMB->>+AD: Validate User/Group Identity
        AD-->>-SMB: User/Group Validation Result
    end

    alt All Users/Groups Valid
        SMB->>+FS: Apply ACL Changes to File System
        FS-->>-SMB: ACL Applied Successfully
        SMB-->>API: ACL Update Successful
        API-->>-Admin: 200 OK (Permissions Updated)
    else Invalid User/Group Found
        SMB-->>API: Validation Failed
        API-->>-Admin: 422 Unprocessable Entity (Invalid User/Group)
    else Domain Connection Failed
        SMB-->>API: Domain Unavailable
        API-->>-Admin: 503 Service Unavailable (Domain Error)
    end

    Admin->>+API: GET /storage/smb-shares/{share_id}/acl
    API-->>-Admin: 200 OK (Verify ACL Changes)
```

## Example with `curl`

```bash
curl -X PATCH "https://netapp.example.com/api/storage/smb-shares/{share_id}/acl" \
     -H "Authorization: Basic <base64_auth_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "acl_entries": [
         {
           "user_or_group": "DOMAIN\\john.doe",
           "permission": "full-control",
           "access_type": "allow"
         },
         {
           "user_or_group": "DOMAIN\\sales_team",
           "permission": "change",
           "access_type": "allow"
         }
       ]
     }'
```

## Output

### Successful Response Examples

#### ACL Update Success (200 OK)

```json
{
  "share_id": "smb_share_001",
  "name": "sales_data",
  "acl_entries": [
    {
      "user_or_group": "DOMAIN\\john.doe",
      "permission": "full-control",
      "access_type": "allow",
      "status": "applied"
    },
    {
      "user_or_group": "DOMAIN\\sales_team",
      "permission": "change",
      "access_type": "allow",
      "status": "applied"
    }
  ],
  "message": "ACL permissions updated successfully"
}
```

### Error Response Examples

#### Authentication Failure (401 Unauthorized)

```json
{
  "error": {
    "code": "401",
    "message": "Authentication failed. Invalid credentials.",
    "target": "authentication"
  }
}
```

#### Insufficient Permissions (403 Forbidden)

```json
{
  "error": {
    "code": "403",
    "message": "Insufficient privileges to modify SMB share permissions. Required privilege: storage-admin.",
    "target": "authorization"
  }
}
```

#### Share Not Found (404 Not Found)

```json
{
  "error": {
    "code": "404",
    "message": "SMB share with ID 'smb_share_001' not found.",
    "target": "share_id"
  }
}
```

#### Invalid User/Group (422 Unprocessable Entity)

```json
{
  "error": {
    "code": "422",
    "message": "User or group 'DOMAIN\\invalid_user' not found in domain.",
    "target": "acl_entries.user_or_group"
  }
}
```

#### Domain Connection Error (503 Service Unavailable)

```json
{
  "error": {
    "code": "503",
    "message": "Unable to connect to domain controller for user validation.",
    "target": "domain_service"
  }
}
```

## Best Practices

### Security

- **Principle of Least Privilege**: Grant minimum necessary permissions
- **Regular Audits**: Review and audit permissions periodically
- **Group-Based Access**: Use domain groups rather than individual users when possible
- **Document Changes**: Maintain audit trail of permission modifications

### Performance

- **Batch Operations**: Group multiple ACL changes in single API calls
- **Validate Before Apply**: Check user/group existence before making changes
- **Monitor Impact**: Watch for performance impact on file access

### Maintenance

- **Cleanup Unused Entries**: Remove obsolete user/group permissions
- **Test Permissions**: Verify access works as expected after changes
- **Backup ACLs**: Maintain backup of critical share permissions

## Error Handling

- **Authentication Issues**: Verify credentials and domain connectivity
- **User/Group Validation**: Confirm users exist in Active Directory
- **Permission Conflicts**: Handle overlapping allow/deny rules appropriately
- **Domain Connectivity**: Implement retry logic for domain controller issues
- **Network Errors**: Use exponential backoff for transient network failures

## Related Operations

- **Create SMB Share**: Provision new SMB shares with initial permissions
- **List Share Permissions**: Retrieve current ACL settings for audit
- **Remove Permissions**: Delete specific ACL entries from shares
- **Bulk Permission Updates**: Apply permission changes across multiple shares
