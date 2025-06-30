# Mermaid Diagram Testing Page

This page contains various Mermaid diagrams to test the MkDocs Mermaid integration and identify any syntax issues.

## 1. Basic Flowchart

```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process 1]
    B -->|No| D[Process 2]
    C --> E[End]
    D --> E
```

## 2. Sequence Diagram

```mermaid
sequenceDiagram
    participant A as Client
    participant B as Server
    participant C as Database

    A->>B: Request
    B->>C: Query
    C-->>B: Response
    B-->>A: Result
```

## 3. Gantt Chart

```mermaid
gantt
    title NetApp Project Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1
    Planning     :a1, 2024-01-01, 30d
    Development  :after a1, 45d
    section Phase 2
    Testing      :2024-03-15, 20d
    Deployment   :2024-04-04, 10d
```

## 4. Class Diagram

```mermaid
classDiagram
    class MCP_Server {
        +str name
        +str version
        +list tools
        +initialize()
        +handle_request()
    }

    class NetApp_API {
        +str base_url
        +str auth_token
        +get_clusters()
        +get_volumes()
    }

    MCP_Server --> NetApp_API : uses
```

## 5. State Diagram

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : request
    Processing --> Success : complete
    Processing --> Error : fail
    Success --> [*]
    Error --> Idle : retry
```

## 6. Entity Relationship Diagram

```mermaid
erDiagram
    CLUSTER ||--o{ SVM : contains
    SVM ||--o{ VOLUME : contains
    VOLUME ||--o{ SNAPSHOT : has

    CLUSTER {
        string uuid
        string name
        string version
    }

    SVM {
        string uuid
        string name
        string type
    }

    VOLUME {
        string uuid
        string name
        int size
    }
```

## 7. User Journey

```mermaid
journey
    title NetApp Storage Admin Journey
    section Discovery
      Login to ActiveIQ: 5: Admin
      View Clusters: 4: Admin
      Check Performance: 3: Admin
    section Action
      Identify Issues: 2: Admin
      Create Volumes: 5: Admin
      Monitor Results: 4: Admin
```

## 8. Git Graph

```mermaid
gitgraph
    commit id: "Initial"
    branch develop
    checkout develop
    commit id: "Feature A"
    commit id: "Feature B"
    checkout main
    merge develop
    commit id: "Release 1.0"
```

## 9. Pie Chart

```mermaid
pie title Storage Utilization
    "Used" : 65
    "Available" : 25
    "Reserved" : 10
```

## 10. Flowchart with Subgraphs

```mermaid
flowchart TD
    subgraph "NetApp Environment"
        A[ActiveIQ Unified Manager]
        B[Cluster 1]
        C[Cluster 2]
    end

    subgraph "MCP Server"
        D[API Gateway]
        E[Authentication]
        F[Tools Handler]
    end

    subgraph "Client Applications"
        G[AI Assistant]
        H[Automation Tools]
        I[Monitoring Dashboard]
    end

    A --> D
    B --> A
    C --> A
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
```

## 11. Complex Sequence with Loops

```mermaid
sequenceDiagram
    participant C as Client
    participant M as MCP Server
    participant N as NetApp API
    participant D as Database

    C->>M: Initialize Connection
    M->>N: Authenticate
    N-->>M: Auth Token

    loop Health Check
        M->>N: Get Cluster Status
        N-->>M: Status Response
    end

    C->>M: Get Volume Info
    M->>N: Query Volumes
    N->>D: Fetch Data
    D-->>N: Volume Data
    N-->>M: Volume Response
    M-->>C: Formatted Result

    Note over C,D: End-to-end data flow
```

## 12. Advanced Flowchart with Styling

```mermaid
flowchart LR
    A[User Request] --> B{Authentication}
    B -->|Valid| C[Process Request]
    B -->|Invalid| D[Return Error]
    C --> E{Request Type}
    E -->|Cluster Info| F[Get Clusters]
    E -->|Volume Info| G[Get Volumes]
    E -->|Performance| H[Get Metrics]
    F --> I[Format Response]
    G --> I
    H --> I
    I --> J[Return Result]
    D --> K[Log Error]

    classDef successClass fill:#d4edda,stroke:#155724,stroke-width:2px
    classDef errorClass fill:#f8d7da,stroke:#721c24,stroke-width:2px
    classDef processClass fill:#fff3cd,stroke:#856404,stroke-width:2px

    class F,G,H,I,J successClass
    class D,K errorClass
    class C,E processClass
```

## 13. Timeline

```mermaid
timeline
    title NetApp MCP Server Development

    2024-Q1 : Planning
             : Requirements Gathering
             : API Analysis

    2024-Q2 : Development
             : Core Implementation
             : Testing Framework

    2024-Q3 : Integration
             : AI Assistant Support
             : Documentation

    2024-Q4 : Production
             : Deployment
             : Monitoring Setup
```

## 14. Mindmap

```mermaid
mindmap
  root((NetApp MCP))
    Clusters
      Performance
      Health
      Configuration
    Volumes
      Storage
      Snapshots
      Quotas
    SVMs
      Protocols
      Security
      Networking
    Tools
      Monitoring
      Automation
      Analysis
```

## Test Status

- ✅ Basic diagrams should render correctly
- ✅ Complex diagrams with subgraphs
- ✅ Styling and theming
- ✅ Various diagram types (flowchart, sequence, gantt, etc.)

## Common Issues to Watch For

1. **Arrow syntax**: Ensure `-->` not `--&gt;` or `--\u003e`
2. **Quote escaping**: Proper handling of quotes in labels
3. **Theme compatibility**: Mermaid v11.4.0 theme variables
4. **Plugin configuration**: mermaid2 plugin settings

## Debugging Commands

To test this page locally:

```bash
# Activate virtual environment
source venv-docs/bin/activate

# Serve the documentation
mkdocs serve

# Build for production
mkdocs build
```

## Version Information

- **Mermaid Version**: 11.4.0
- **Plugin**: mkdocs-mermaid2-plugin 1.2.1
- **MkDocs**: 1.6.1
- **Material Theme**: 9.6.14

## Mermaid Configuration Test

Current plugin configuration from mkdocs.yml:

```yaml
- mermaid2:
    version: '11.4.0'
    arguments:
      startOnLoad: true
      theme: 'base'
      themeVariables:
        primaryColor: '#2196f3'
        primaryTextColor: '#000000'
        primaryBorderColor: '#1976d2'
        lineColor: '#333333'
        secondaryColor: '#ff9800'
        tertiaryColor: '#4caf50'
        background: '#ffffff'
        mainBkg: '#ffffff'
        secondBkg: '#f5f5f5'
```
