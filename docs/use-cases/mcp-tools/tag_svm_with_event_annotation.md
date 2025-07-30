# Use Case: Tagging an SVM via Event Annotation

This sequence diagram illustrates how to tag an SVM by creating a new event and adding a custom annotation to it.

```mermaid
sequenceDiagram
    participant AS as Automation Script
    participant API as NetApp ActiveIQ API

    AS->>+API: Authenticate (HTTP Basic Auth)
    API-->>-AS: 200 OK (Authentication Successful)

    Note over AS, API: All subsequent requests are authenticated

    AS->>+API: GET /datacenter/svm/svms (Find SVM)
    API-->>-AS: 200 OK (List of SVMs)

    Note right of AS: Prepare event payload<br/>with SVM key and<br/>custom annotation

    AS->>+API: POST /management-server/events (Create Event with Annotation)
    API-->>-AS: 202 Accepted (Job Key)

    loop Poll Job Status
        AS->>+API: GET /management-server/jobs/{job_key}
        API-->>-AS: 200 OK (Job Status)
    end

    AS->>+API: GET /management-server/events/{event_key} (Verify Annotation)
    API-->>-AS: 200 OK (Event with SVM and Annotation)
```

### Error Handling

- **Authentication Failure (401 Unauthorized)**: If authentication fails, the script should log the error and terminate. Ensure that the API credentials are correct and have the necessary permissions.
- **SVM Not Found (404 Not Found)**: If the SVM to be tagged does not exist, the script should handle the error gracefully.
- **Invalid Event Payload (400 Bad Request)**: If the event creation request is invalid (e.g., missing required fields), the API will return a 400 error. The script should validate the payload before sending it.
- **Job Failure**: The event creation job may fail. The script should monitor the job status and provide detailed error information if it fails.
- **Network Errors**: Implement retry logic with exponential backoff for transient network errors.
