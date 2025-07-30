# Use Case: Apply Snapshot Policy to Volume

## Overview

This use case describes how to apply an existing Snapshot policy to a Volume using the NetApp API. Once applied, the volume will follow the snapshot schedule and retention rules defined in the policy.

## API Endpoint

- **PATCH** `/api/storage/volumes/{volume_uuid}`
- **Permissions**: `cluster-admin` or `volume-admin`

## Prerequisites

1. The snapshot policy must exist in the cluster
2. The target volume must exist and be accessible
3. Sufficient space must be available for snapshots

## Request Body

The request body should specify the snapshot policy to apply to the volume:

```json
{
  "snapshot_policy": {
    "name": "Daily_and_Weekly_Snapshots"
  }
}
```

## Example with `curl`

Here's how you can apply a snapshot policy to a volume using `curl`:

```bash
# First, get the volume UUID
curl -X GET "https://<netapp-ip>/api/storage/volumes?name=<volume_name>" \
     -H "Authorization: Basic <base64_auth_token>" \
     -H "Content-Type: application/json"

# Then apply the policy using the UUID
curl -X PATCH "https://<netapp-ip>/api/storage/volumes/<volume_uuid>" \
     -H "Authorization: Basic <base64_auth_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "snapshot_policy": {
         "name": "Daily_and_Weekly_Snapshots"
       }
     }'
```

## Complete Example Script

Here's a complete bash script that finds a volume by name and applies a snapshot policy:

```bash
#!/bin/bash

NETAPP_IP="your-netapp-cluster-ip"
AUTH_TOKEN="your-base64-auth-token"
VOLUME_NAME="volume_prod_data"
POLICY_NAME="Daily_and_Weekly_Snapshots"

# Get volume UUID
VOLUME_UUID=$(curl -s -X GET "https://${NETAPP_IP}/api/storage/volumes?name=${VOLUME_NAME}" \
  -H "Authorization: Basic ${AUTH_TOKEN}" \
  -H "Content-Type: application/json" | \
  jq -r '.records[0].uuid')

if [ "$VOLUME_UUID" = "null" ]; then
  echo "Volume $VOLUME_NAME not found"
  exit 1
fi

echo "Found volume UUID: $VOLUME_UUID"

# Apply snapshot policy
curl -X PATCH "https://${NETAPP_IP}/api/storage/volumes/${VOLUME_UUID}" \
     -H "Authorization: Basic ${AUTH_TOKEN}" \
     -H "Content-Type: application/json" \
     -d "{
       \"snapshot_policy\": {
         \"name\": \"${POLICY_NAME}\"
       }
     }"

echo "Snapshot policy '${POLICY_NAME}' applied to volume '${VOLUME_NAME}'"
```

## Verification

To verify that the snapshot policy has been applied successfully:

```bash
curl -X GET "https://<netapp-ip>/api/storage/volumes/<volume_uuid>?fields=snapshot_policy" \
     -H "Authorization: Basic <base64_auth_token>" \
     -H "Content-Type: application/json"
```

## Best Practices

- Verify that the snapshot policy exists before applying it to a volume
- Monitor the volume's available space after applying snapshot policies
- Consider the performance impact of frequent snapshots on high-throughput volumes
- Test snapshot policies on non-production volumes first
- Document which volumes use which snapshot policies for easier management

## Error Handling

Common errors when applying snapshot policies:

- **404 Not Found**: The volume UUID or snapshot policy name doesn't exist
- **403 Forbidden**: Insufficient permissions to modify the volume
- **400 Bad Request**: Invalid policy name or malformed request body

Always check the API response for error details and handle them appropriately in your automation scripts.
