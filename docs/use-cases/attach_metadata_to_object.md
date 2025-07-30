# Use Case: Attaching Metadata to any Object

This sequence diagram illustrates a generic process for attaching metadata to any object (e.g., SVM, LUN, file share) by creating an associated event with a custom annotation.

```mermaid
sequenceDiagram
    participant User as User/Admin
    participant Console as ActiveIQ Unified Manager
    participant API as NetApp ActiveIQ API

    User->>+Console: 1. Log in to ActiveIQ Console
    Console-->>-User: Authentication Successful

    User->>+Console: 2. Navigate to Object Explorer
    Console-->>-User: Display Object Inventory (SVMs, LUNs, etc.)

    User->>+Console: 3. Select Object to Tag
    Console-->>-User: Display Object Details

    User->>+Console: 4. Initiate "Add Annotation" Action
    Note right of Console: Console prepares event creation request<br/>with object key and user-provided metadata
    Console->>+API: 5. POST /management-server/events (Create Event)
    API-->>-Console: 202 Accepted (Job Key)

    loop Poll Job Status
        Console->>+API: GET /management-server/jobs/{job_key}
        API-->>-Console: 200 OK (Job Status)
    end

    Console->>+User: 6. Display Confirmation (Annotation Added)

    User->>+Console: 7. View Object Annotations
    Console->>+API: 8. GET /management-server/events?resource.key={object_key}
    API-->>-Console: 200 OK (List of Events with Annotations)
    Console-->>-User: Display Associated Annotations
```

### Error Handling

- **Object Not Found (404 Not Found)**: If the target object for annotation does not exist, the console should provide a user-friendly error message.
- **Invalid Metadata (400 Bad Request)**: The console should validate the metadata format (e.g., key-value pairs) before submitting the request to the API.
- **Permission Denied (403 Forbidden)**: If the user does not have the necessary permissions to create events or annotate objects, the console should display an access denied message.
- **Job Failure**: If the event creation job fails, the console should provide detailed error information to help the user diagnose the issue.
- **Concurrent Modifications (409 Conflict)**: If the object is being modified by another user, the console should handle the conflict gracefully, perhaps by asking the user to retry.
