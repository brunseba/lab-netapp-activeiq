# Use Case: Provisioning a New NFS File Share

This sequence diagram illustrates the process of authenticating, discovering resources, provisioning a new NFS file share, and monitoring the creation job.

```mermaid
sequenceDiagram
    participant AS as Automation Script
    participant API as NetApp ActiveIQ API

    AS->>+API: Authenticate (HTTP Basic Auth)
    API-->>-AS: 200 OK (Authentication Successful)

    Note over AS, API: All subsequent requests are authenticated

    AS->>+API: GET /datacenter/cluster/clusters (Discover Clusters)
    API-->>-AS: 200 OK (List of Clusters)

    AS->>+API: GET /storage-provider/svms?cluster.key={key} (Discover SVMs)
    API-->>-AS: 200 OK (List of SVMs)

    AS->>+API: GET /datacenter/storage/aggregates?cluster.key={key} (Discover Aggregates)
    API-->>-AS: 200 OK (List of Aggregates)

    AS->>+API: POST /storage-provider/file-shares (Create File Share)
    API-->>-AS: 202 Accepted (Job Key)

    loop Poll Job Status
        AS->>+API: GET /management-server/jobs/{job_key}
        API-->>-AS: 200 OK (Job Status)
    end

    AS->>+API: GET /storage-provider/file-shares/{fileshare_key} (Get File Share Details)
    API-->>-AS: 200 OK (File Share Details)
```

### Error Handling

- **Authentication Failure (401 Unauthorized)**: If authentication fails, the script should log the error and terminate. Ensure that the API credentials are correct and have the necessary permissions.
- **Resource Not Found (404 Not Found)**: If a cluster, SVM, or aggregate is not found, the script should handle the error gracefully. This could involve trying a different resource or logging the error and exiting.
- **Invalid Request (400 Bad Request)**: If the `POST` request to create the file share is invalid, the API will return a 400 error with a descriptive message. The script should parse the error message and provide feedback to the user.
- **Job Failure**: The job to create the file share may fail for various reasons (e.g., insufficient space, configuration error). The script should monitor the job status and, if it fails, retrieve the job's error message to diagnose the problem.
- **Network Errors**: Implement retry logic with exponential backoff for transient network errors (e.g., timeouts, connection errors).
