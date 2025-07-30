# Use Case: Annotating an Event

This sequence diagram illustrates how to authenticate, find an event, and then add or update an annotation.

## Adding a New Annotation

```mermaid
sequenceDiagram
    participant AS as Automation Script
    participant API as NetApp ActiveIQ API

    AS->>+API: Authenticate (HTTP Basic Auth)
    API-->>-AS: 200 OK (Authentication Successful)

    Note over AS, API: All subsequent requests are authenticated

    AS->>+API: GET /management-server/events (Find Event)
    API-->>-AS: 200 OK (List of Events)

    AS->>+API: PATCH /management-server/events/{key} (Add Annotation)
    API-->>-AS: 200 OK (Event with Annotation)
```

## Updating an Existing Annotation

```mermaid
sequenceDiagram
    participant AS as Automation Script
    participant API as NetApp ActiveIQ API

    AS->>+API: Authenticate (HTTP Basic Auth)
    API-->>-AS: 200 OK (Authentication Successful)

    Note over AS, API: All subsequent requests are authenticated

    AS->>+API: GET /management-server/events/{key} (Get Current Event)
    API-->>-AS: 200 OK (Event with Current Annotation)

    Note right of AS: Parse existing annotation<br/>Merge or replace with new values

    AS->>+API: PATCH /management-server/events/{key} (Update Annotation)
    API-->>-AS: 200 OK (Event with Updated Annotation)

    AS->>+API: GET /management-server/events/{key} (Verify Update)
    API-->>-AS: 200 OK (Event with New Annotation)
```

### Error Handling

- **Authentication Failure (401 Unauthorized)**: If authentication fails, the script should log the error and terminate. Ensure that the API credentials are correct and have the necessary permissions.
- **Event Not Found (404 Not Found)**: If the event to be annotated is not found, the script should handle the error gracefully. This could involve logging the error and moving on to the next event.
- **Invalid Annotation (400 Bad Request)**: If the annotation format is invalid, the API will return a 400 error. The script should ensure that the annotation is a simple string.
- **Forbidden (403 Forbidden)**: If the user doesn't have permissions to modify the event, the script should log the error and notify the administrator.
- **Conflict (409 Conflict)**: If another process is modifying the same event simultaneously, the API may return a 409 error. The script should implement retry logic with backoff to handle this.
- **Network Errors**: Implement retry logic with exponential backoff for transient network errors.
