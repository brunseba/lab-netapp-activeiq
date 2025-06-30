# NetApp ActiveIQ MCP Server - Technical Documentation

## Overview

This document provides comprehensive technical documentation for the NetApp ActiveIQ MCP Server, including detailed component models, sequence diagrams, and architectural patterns for the Temporal.io-powered durable execution system.

## Component Model (CMP-XXXX)

### Component Registry

| **Component ID** | **Component Name** | **Type** | **Purpose** | **Dependencies** |
|------------------|-------------------|----------|-------------|------------------|
| **CMP-0001** | AI Assistant Interface | External | Natural language processing and user interaction | Claude Desktop, Custom AI Apps |
| **CMP-0002** | MCP Protocol Gateway | Service | MCP protocol handling and routing | CMP-0003, CMP-0004 |
| **CMP-0003** | Request Router | Service | Route MCP requests to appropriate handlers | CMP-0005, CMP-0006 |
| **CMP-0004** | Schema Validator | Service | Validate MCP messages and tool arguments | JSON Schema Library |
| **CMP-0005** | Tool Registry | Service | Manage and discover available MCP tools | CMP-0008, CMP-0009 |
| **CMP-0006** | Response Formatter | Service | Format responses according to MCP specification | CMP-0003 |
| **CMP-0007** | Authentication Manager | Service | Handle NetApp API authentication and security | CMP-0010, CMP-0015 |
| **CMP-0008** | NetApp API Client | Service | Interface with ActiveIQ Unified Manager API | CMP-0007, CMP-0016 |
| **CMP-0009** | Temporal Workflow Engine | Platform | Orchestrate durable, fault-tolerant workflows | CMP-0010, CMP-0011, CMP-0012 |
| **CMP-0010** | Workflow Activities | Service | Execute individual NetApp operations | CMP-0008, CMP-0013 |
| **CMP-0011** | Temporal Workers | Service | Process workflow activities and maintain state | CMP-0009, CMP-0010 |
| **CMP-0012** | Workflow State Store | Data | Persist workflow state and execution history | PostgreSQL Database |
| **CMP-0013** | Cache Manager | Service | Manage response caching and performance optimization | Redis, CMP-0008 |
| **CMP-0014** | Event Processor | Service | Handle NetApp events and trigger workflows | CMP-0009, CMP-0016 |
| **CMP-0015** | Security Context | Service | Manage credentials, certificates, and access control | Kubernetes Secrets, Vault |
| **CMP-0016** | NetApp Infrastructure | External | ActiveIQ Unified Manager and ONTAP clusters | External NetApp Systems |
| **CMP-0017** | Knative Serving | Platform | Serverless container orchestration and auto-scaling | Kubernetes, Istio/Kourier |
| **CMP-0018** | Monitoring Stack | Platform | Observability, metrics, and alerting | Prometheus, Grafana, Jaeger |
| **CMP-0019** | Configuration Manager | Service | Manage environment-specific configurations | ConfigMaps, Secrets |
| **CMP-0020** | Health Monitor | Service | System health checks and readiness probes | CMP-0008, CMP-0009, CMP-0013 |

### Component Architecture Diagram

```mermaid
graph TB
    subgraph "External Layer"
        CMP0001[CMP-0001: AI Assistant Interface]
        CMP0016[CMP-0016: NetApp Infrastructure]
    end

    subgraph "API Gateway Layer"
        CMP0002[CMP-0002: MCP Protocol Gateway]
        CMP0003[CMP-0003: Request Router]
        CMP0004[CMP-0004: Schema Validator]
        CMP0006[CMP-0006: Response Formatter]
    end

    subgraph "Service Layer"
        CMP0005[CMP-0005: Tool Registry]
        CMP0007[CMP-0007: Authentication Manager]
        CMP0008[CMP-0008: NetApp API Client]
        CMP0013[CMP-0013: Cache Manager]
        CMP0014[CMP-0014: Event Processor]
        CMP0020[CMP-0020: Health Monitor]
    end

    subgraph "Workflow Orchestration Layer"
        CMP0009[CMP-0009: Temporal Workflow Engine]
        CMP0010[CMP-0010: Workflow Activities]
        CMP0011[CMP-0011: Temporal Workers]
    end

    subgraph "Data Layer"
        CMP0012[CMP-0012: Workflow State Store]
    end

    subgraph "Platform Layer"
        CMP0017[CMP-0017: Knative Serving]
        CMP0015[CMP-0015: Security Context]
        CMP0018[CMP-0018: Monitoring Stack]
        CMP0019[CMP-0019: Configuration Manager]
    end

    CMP0001 --> CMP0002
    CMP0002 --> CMP0003
    CMP0003 --> CMP0004
    CMP0003 --> CMP0005
    CMP0003 --> CMP0006
    CMP0005 --> CMP0009
    CMP0007 --> CMP0008
    CMP0008 --> CMP0016
    CMP0009 --> CMP0010
    CMP0009 --> CMP0011
    CMP0009 --> CMP0012
    CMP0010 --> CMP0008
    CMP0010 --> CMP0013
    CMP0011 --> CMP0012
    CMP0014 --> CMP0009
    CMP0016 --> CMP0014
```

## Detailed Sequence Diagrams

### 1. Simple Volume Creation Workflow (DevOps GUI Primary)

```mermaid
sequenceDiagram
    participant DevOps as DevOps GUI
    participant APIM as API Management
    participant Temporal as CMP-0009: Temporal Engine
    participant Worker as CMP-0011: Temporal Worker
    participant Activities as CMP-0010: Workflow Activities
    participant MCP as CMP-0002: MCP Gateway (Optional)
    participant Client as CMP-0008: NetApp Client
    participant NetApp as CMP-0016: NetApp Infrastructure

    Note over DevOps,NetApp: DevOps-Driven Volume Creation (2-3 minutes)

    DevOps->>APIM: POST /api/v1/workflows/create-volume
    Note right of DevOps: {"name": "db-vol-001", "size": "500GB", "svm": "prod-svm"}

    APIM->>Temporal: Start VolumeCreation Workflow
    Temporal->>Worker: Assign Volume Creation Task

    Worker->>Activities: Execute validate_volume_request
    Activities->>Client: Validate Volume Parameters
    Client->>NetApp: GET /datacenter/storage/aggregates
    NetApp-->>Client: Available Aggregates
    Activities-->>Worker: Validation Complete

    Worker->>Activities: Execute create_volume_activity

    alt MCP Integration Available
        Activities->>MCP: Call MCP create_volume tool
        MCP->>Client: Execute NetApp API Call
    else Direct API Integration
        Activities->>Client: Direct NetApp API Call
    end

    Client->>NetApp: POST /datacenter/storage/volumes
    Note right of Client: Create volume with optimal aggregate
    NetApp-->>Client: Volume Created (UUID: vol-123)

    Client->>NetApp: GET /datacenter/storage/volumes/vol-123
    NetApp-->>Client: Volume Details

    Activities-->>Worker: Volume Creation Complete
    Worker-->>Temporal: Workflow Success
    Temporal-->>APIM: Volume Created Response
    APIM-->>DevOps: Volume: db-vol-001 (500GB) created successfully

    Note over DevOps: DevOps validates volume creation in GUI dashboard
```

### 2. Complex SVM Environment Setup with Temporal (DevOps Primary)

```mermaid
sequenceDiagram
    participant DevOps as DevOps GUI
    participant APIM as API Management
    participant Temporal as CMP-0009: Temporal Engine
    participant Worker as CMP-0011: Temporal Worker
    participant Activities as CMP-0010: Workflow Activities
    participant Client as CMP-0008: NetApp Client
    participant State as CMP-0012: State Store
    participant NetApp as CMP-0016: NetApp Infrastructure
    participant EventProc as CMP-0014: Event Processor

    Note over DevOps,EventProc: DevOps-Driven SVM Environment Setup (30-45 minutes)

    DevOps->>APIM: POST /api/v1/workflows/svm-environment-setup
    Note right of DevOps: {"team": "mobile-dev", "environment": "development", "protocols": ["nfs", "cifs"]}

    APIM->>Temporal: Start SVMEnvironmentSetup Workflow

    Temporal->>State: Persist Workflow State
    State-->>Temporal: State Saved

    Temporal->>Worker: Assign Workflow
    Worker->>Activities: Execute validate_requirements

    Activities->>Client: Validate Team Requirements
    Client->>NetApp: GET /datacenter/cluster/clusters
    NetApp-->>Client: Cluster Information
    Activities-->>Worker: Validation Complete

    Worker->>State: Update Workflow State
    Worker->>Activities: Execute allocate_resources

    Activities->>Client: Find Optimal Resources
    Client->>NetApp: GET /datacenter/storage/aggregates
    NetApp-->>Client: Available Aggregates
    Activities-->>Worker: Resources Allocated

    Worker->>State: Update Workflow State
    Worker->>Activities: Execute create_svm

    Activities->>Client: Create SVM
    Client->>NetApp: POST /datacenter/svm/svms
    NetApp-->>Client: SVM Created (UUID: svm-456)
    Activities-->>Worker: SVM Creation Complete

    Worker->>State: Update Workflow State

    par Parallel Network Configuration
        Worker->>Activities: Execute create_management_lif
        Activities->>Client: Create Management LIF
        Client->>NetApp: POST /network/ip/interfaces
        NetApp-->>Client: Management LIF Created
        Activities-->>Worker: Management LIF Ready
    and
        Worker->>Activities: Execute create_data_lifs
        Activities->>Client: Create Data LIFs
        Client->>NetApp: POST /network/ip/interfaces (x2)
        NetApp-->>Client: Data LIFs Created
        Activities-->>Worker: Data LIFs Ready
    end

    Worker->>State: Update Workflow State
    Worker->>Activities: Execute provision_volumes

    Activities->>Client: Create Development Volumes
    Client->>NetApp: POST /datacenter/storage/volumes (x3)
    NetApp-->>Client: Volumes Created
    Activities-->>Worker: Volumes Provisioned

    Worker->>State: Update Workflow State
    Worker->>Activities: Execute configure_snapshots

    Activities->>Client: Configure Snapshot Policies
    Client->>NetApp: POST /storage/snapshot-policies
    NetApp-->>Client: Policies Configured
    Activities-->>Worker: Snapshots Configured

    Worker->>State: Update Workflow State
    Worker->>Activities: Execute finalize_setup

    Activities->>Client: Final Configuration
    Client->>NetApp: Multiple API calls for final config
    NetApp-->>Client: Configuration Complete
    Activities-->>Worker: Setup Finalized

    Worker->>State: Update Final Workflow State
    Worker->>Activities: Execute send_notification

    Activities->>EventProc: Send Team Notification
    EventProc-->>Activities: Notification Sent

    Worker-->>Temporal: Workflow Complete
    Temporal-->>Router: SVM Environment Ready
    Router-->>Gateway: Environment Setup Complete
    Gateway-->>AI: Development environment ready for mobile-dev team

    Note over AI: Complete environment with SVM, networks, volumes, and policies ready
```

### 3. Event-Driven Capacity Management (Day-2 AI Integration)

```mermaid
sequenceDiagram
    participant NetApp as CMP-0016: NetApp Infrastructure
    participant EventProc as CMP-0014: Event Processor
    participant APIM as API Management
    participant Temporal as CMP-0009: Temporal Engine
    participant Worker as CMP-0011: Temporal Worker
    participant Activities as CMP-0010: Workflow Activities
    participant Client as CMP-0008: NetApp Client
    participant Monitor as CMP-0020: Health Monitor
    participant AI as CMP-0001: AI Assistant (Day-2)

    Note over NetApp,AI: Continuous Capacity Management with Day-2 AI

    loop Every Hour
        Temporal->>Worker: Execute capacity_check_activity
        Worker->>Activities: Check Cluster Capacity
        Activities->>Client: Get Capacity Metrics
        Client->>NetApp: GET /datacenter/storage/aggregates
        NetApp-->>Client: Capacity Data
        Activities-->>Worker: Capacity Status: 75% Used
        Worker-->>Temporal: Normal Capacity
        Temporal->>Temporal: Sleep 1 Hour
    end

    Note over NetApp: Capacity reaches 85%

    NetApp->>EventProc: Capacity Alert Event
    EventProc->>APIM: Forward Alert to API Management
    APIM->>Temporal: Signal: high_capacity_alert

    Temporal->>Worker: Trigger Capacity Analysis
    Worker->>Activities: Execute detailed_capacity_analysis

    Activities->>Client: Analyze Capacity Trends
    Client->>NetApp: GET /gateways/clusters/{uuid}/metrics/aggregates/perf
    NetApp-->>Client: Historical Performance Data

    Activities->>Client: Get Volume Growth Patterns
    Client->>NetApp: GET /datacenter/storage/volumes?fields=size,growth
    NetApp-->>Client: Volume Growth Data

    Activities-->>Worker: Analysis: Need 2TB Additional Capacity

    Worker->>Activities: Execute generate_expansion_plan
    Activities->>Client: Create Expansion Recommendations
    Client->>NetApp: GET /datacenter/storage/disks?available=true
    NetApp-->>Client: Available Disk Information

    Activities-->>Worker: Expansion Plan Ready

    Worker->>Activities: Execute request_approval
    Activities->>APIM: Send Approval Request via API
    APIM->>AI: Forward to AI Assistant (Day-2 Operation)
    Note right of APIM: "Cluster prod-01 needs 2TB expansion. AI approval?"

    AI-->>APIM: AI Analysis & Approval: APPROVED
    APIM-->>Activities: Approval: APPROVED

    Worker->>Activities: Execute capacity_expansion
    Activities->>Client: Add Disks to Aggregate
    Client->>NetApp: POST /datacenter/storage/aggregates/{id}/disks
    NetApp-->>Client: Expansion In Progress

    Activities->>Monitor: Monitor Expansion Progress
    Monitor->>Client: Check Expansion Status
    Client->>NetApp: GET /management-server/jobs/{job-id}
    NetApp-->>Client: Job Status: COMPLETED
    Monitor-->>Activities: Expansion Complete

    Activities-->>Worker: Capacity Expansion Successful
    Worker->>Activities: Execute send_completion_notification

    Activities->>APIM: Send Completion Notification
    APIM->>AI: Forward to AI Assistant (Day-2 Update)
    Note right of APIM: "Capacity expansion completed. 2TB added to prod-01"

    Worker-->>Temporal: Capacity Management Cycle Complete

    Note over Temporal: Resume Normal Monitoring
```

### 4. Failure Recovery and Retry Mechanism (DevOps Primary)

```mermaid
sequenceDiagram
    participant DevOps as DevOps GUI
    participant APIM as API Management
    participant Temporal as CMP-0009: Temporal Engine
    participant Worker as CMP-0011: Temporal Worker
    participant Activities as CMP-0010: Workflow Activities
    participant Client as CMP-0008: NetApp Client
    participant State as CMP-0012: State Store
    participant NetApp as CMP-0016: NetApp Infrastructure

    Note over DevOps,NetApp: DevOps SVM Creation with Failure Recovery

    DevOps->>APIM: Start SVM Creation via GUI
    APIM->>Temporal: Start SVM Creation Workflow
    Temporal->>State: Persist Initial State

    Temporal->>Worker: Execute Workflow
    Worker->>Activities: validate_cluster_health
    Activities->>Client: Check Cluster Health
    Client->>NetApp: GET /datacenter/cluster/clusters/{id}
    NetApp-->>Client: Cluster Healthy
    Activities-->>Worker: Validation Success

    Worker->>State: Update: validation_complete
    Worker->>Activities: create_svm
    Activities->>Client: Create SVM
    Client->>NetApp: POST /datacenter/svm/svms

    Note over NetApp: Network Timeout
    NetApp-->>Client: ERROR: Connection Timeout
    Client-->>Activities: Network Error
    Activities-->>Worker: Activity Failed

    Worker->>State: Update: create_svm_failed (attempt 1)
    Worker->>Temporal: Report Activity Failure

    Note over Temporal: Automatic Retry with Exponential Backoff
    Temporal->>Temporal: Wait 2 seconds

    Temporal->>Worker: Retry create_svm (attempt 2)
    Worker->>Activities: create_svm (retry)
    Activities->>Client: Create SVM (retry)
    Client->>NetApp: POST /datacenter/svm/svms
    NetApp-->>Client: SVM Created Successfully
    Activities-->>Worker: SVM Creation Success

    Worker->>State: Update: svm_created
    Worker->>Activities: configure_network
    Activities->>Client: Configure Network Interfaces
    Client->>NetApp: POST /network/ip/interfaces

    Note over Client: Worker Pod Crashes
    Client-->>Activities: [Connection Lost]

    Note over Temporal: Worker Failure Detected
    Temporal->>State: Read Last Known State
    State-->>Temporal: State: svm_created, network_pending

    Note over Temporal: New Worker Assigned
    Temporal->>Worker: Resume from configure_network
    Worker->>State: Read Current State
    State-->>Worker: SVM UUID: svm-789, Status: created

    Worker->>Activities: configure_network (resume)
    Activities->>Client: Configure Network Interfaces
    Client->>NetApp: POST /network/ip/interfaces
    NetApp-->>Client: Network Configured
    Activities-->>Worker: Network Configuration Success

    Worker->>State: Update: network_configured
    Worker->>Activities: finalize_svm
    Activities->>Client: Final SVM Configuration
    Client->>NetApp: PATCH /datacenter/svm/svms/{id}
    NetApp-->>Client: SVM Finalized
    Activities-->>Worker: Finalization Complete

    Worker->>State: Update: workflow_complete
    Worker-->>Temporal: Workflow Success
    Temporal-->>APIM: SVM Created Successfully
    APIM-->>DevOps: SVM Creation Complete

    Note over DevOps: SVM creation completed despite network timeout and worker failure
```

### 5. Human-in-the-Loop Approval Workflow (DevOps + AI Day-2)

```mermaid
sequenceDiagram
    participant DevOps as DevOps GUI
    participant APIM as API Management
    participant Temporal as CMP-0009: Temporal Engine
    participant Worker as CMP-0011: Temporal Worker
    participant Activities as CMP-0010: Workflow Activities
    participant Client as CMP-0008: NetApp Client
    participant State as CMP-0012: State Store
    participant NetApp as CMP-0016: NetApp Infrastructure
    participant Approver as External: Human Approver
    participant AI as CMP-0001: AI Assistant (Day-2)
    participant Notification as External: Notification System

    Note over DevOps,Notification: DevOps Production SVM Creation with AI-Assisted Approval

    DevOps->>APIM: Create Production SVM Request
    Note right of DevOps: Environment: "production"
    APIM->>Temporal: Create Production SVM Workflow

    Temporal->>State: Persist Workflow State
    Temporal->>Worker: Execute Workflow

    Worker->>Activities: validate_production_requirements
    Activities->>Client: Validate Production Setup
    Client->>NetApp: Multiple validation API calls
    NetApp-->>Client: Validation Results
    Activities-->>Worker: Requirements Valid

    Worker->>State: Update: validation_complete
    Worker->>Activities: prepare_svm_config
    Activities->>Client: Generate Production Configuration
    Client->>NetApp: GET cluster and aggregate information
    NetApp-->>Client: Infrastructure Data
    Activities-->>Worker: Configuration Prepared

    Worker->>State: Update: config_prepared
    Worker->>Activities: request_production_approval

    Activities->>APIM: Send Approval Request
    APIM->>Notification: Forward Approval Request
    Note right of APIM: "Production SVM 'finance-prod' ready for creation. Requires approval."

    Notification->>Approver: Email/Slack Notification
    Note right of Notification: "Approve production SVM creation?"

    par Human Approval Process
        Activities->>State: Update: awaiting_approval
        Worker->>Temporal: Activity Running (wait for approval)

        Note over Temporal: Workflow waits up to 24 hours for approval

        loop Wait for Approval
            Temporal->>State: Check Approval Status
            State-->>Temporal: Status: awaiting_approval
            Temporal->>Temporal: Sleep 30 seconds
        end
    and AI-Assisted Analysis (Day-2)
        APIM->>AI: Request AI Analysis of SVM Config
        AI->>Client: Analyze NetApp Infrastructure
        Client->>NetApp: GET cluster capacity and performance
        NetApp-->>Client: Infrastructure data
        AI-->>APIM: AI Recommendation: "Approved - optimal configuration"
    end

    Note over Approver: Approver reviews request with AI recommendation (after 2 hours)

    Approver->>Notification: APPROVE (based on AI analysis)
    Notification->>APIM: Approval Signal: APPROVED
    APIM->>Activities: Approval Signal: APPROVED
    Activities-->>Worker: Approval Received

    Worker->>State: Update: approved
    Worker->>Activities: create_production_svm

    Activities->>Client: Create Production SVM
    Client->>NetApp: POST /datacenter/svm/svms
    Note right of Client: Production-grade configuration
    NetApp-->>Client: SVM Created (UUID: svm-prod-001)

    Activities-->>Worker: Production SVM Created

    Worker->>Activities: configure_production_security
    Activities->>Client: Apply Security Policies
    Client->>NetApp: Configure LDAP, export policies, etc.
    NetApp-->>Client: Security Configured

    Worker->>Activities: setup_monitoring
    Activities->>Client: Enable Production Monitoring
    Client->>NetApp: Configure alerts and monitoring
    NetApp-->>Client: Monitoring Active

    Worker->>State: Update: workflow_complete
    Worker->>Activities: send_completion_notification

    Activities->>APIM: Send Success Notification
    APIM->>Notification: Forward Success Notification
    Notification->>AI: Production SVM Ready (Day-2 Update)
    Notification->>Approver: Creation Completed

    Worker-->>Temporal: Workflow Complete
    Temporal-->>APIM: Production SVM 'finance-prod' created and ready
    APIM-->>DevOps: SVM Creation Complete

    Note over DevOps: Production environment ready with full approval trail and AI assistance
```

### 6. Multi-Site Data Replication Setup (DevOps Primary)

```mermaid
sequenceDiagram
    participant DevOps as DevOps GUI
    participant APIM as API Management
    participant Temporal as CMP-0009: Temporal Engine
    participant Worker as CMP-0011: Temporal Worker
    participant Activities as CMP-0010: Workflow Activities
    participant Client as CMP-0008: NetApp Client
    participant State as CMP-0012: State Store
    participant PrimarySite as Primary: Primary NetApp Cluster
    participant SecondarySite as Secondary: Secondary NetApp Cluster
    participant Monitor as CMP-0020: Health Monitor

    Note over DevOps,Monitor: DevOps Multi-Site SnapMirror Replication Setup

    DevOps->>APIM: Setup Disaster Recovery Replication
    Note right of DevOps: Source: "prod-vol-001", Target Site: "dr-site"
    APIM->>Temporal: Setup Disaster Recovery Replication

    Temporal->>State: Persist Workflow State
    Temporal->>Worker: Execute Multi-Site Replication Workflow

    Worker->>Activities: validate_source_volume
    Activities->>Client: Validate Source Volume
    Client->>PrimarySite: GET /datacenter/storage/volumes/prod-vol-001
    PrimarySite-->>Client: Volume Details
    Activities-->>Worker: Source Volume Valid

    Worker->>State: Update: source_validated
    Worker->>Activities: validate_destination_cluster
    Activities->>Client: Check Destination Cluster
    Client->>SecondarySite: GET /datacenter/cluster/clusters
    SecondarySite-->>Client: Cluster Status: Healthy
    Activities-->>Worker: Destination Valid

    Worker->>State: Update: destination_validated
    Worker->>Activities: check_network_connectivity

    par Check Inter-Cluster Connectivity
        Activities->>Client: Test Primary to Secondary
        Client->>PrimarySite: GET /network/ip/interfaces
        PrimarySite-->>Client: Network Interfaces
        Client->>SecondarySite: POST /network/ping-test
        SecondarySite-->>Client: Connectivity OK
    and
        Activities->>Client: Check Bandwidth
        Client->>PrimarySite: GET /gateways/clusters/{id}/metrics/network/perf
        PrimarySite-->>Client: Network Performance Metrics
    end

    Activities-->>Worker: Network Connectivity Verified

    Worker->>State: Update: network_verified
    Worker->>Activities: create_destination_volume

    Activities->>Client: Create DP Volume on Secondary
    Client->>SecondarySite: POST /datacenter/storage/volumes
    Note right of Client: Type: DP (Data Protection)
    SecondarySite-->>Client: DP Volume Created (UUID: dp-vol-001)

    Activities-->>Worker: Destination Volume Ready

    Worker->>State: Update: destination_created
    Worker->>Activities: establish_snapmirror_relationship

    Activities->>Client: Create SnapMirror Relationship
    Client->>PrimarySite: POST /snapmirror/relationships
    Note right of Client: Source: prod-vol-001, Destination: dp-vol-001
    PrimarySite-->>Client: Relationship Created (UUID: sm-rel-001)

    Activities-->>Worker: SnapMirror Relationship Established

    Worker->>State: Update: relationship_created
    Worker->>Activities: initialize_snapmirror

    Activities->>Client: Start Initial Transfer
    Client->>PrimarySite: POST /snapmirror/relationships/sm-rel-001/transfers
    PrimarySite-->>Client: Transfer Started (Job: job-123)

    Activities->>Monitor: Monitor Initial Transfer

    loop Monitor Transfer Progress
        Monitor->>Client: Check Transfer Status
        Client->>PrimarySite: GET /management-server/jobs/job-123
        PrimarySite-->>Client: Progress: 45% Complete
        Monitor->>State: Update Progress
        Monitor->>Monitor: Wait 60 seconds
    end

    PrimarySite-->>Client: Transfer Complete
    Monitor-->>Activities: Initial Transfer Successful

    Worker->>State: Update: initialized
    Worker->>Activities: configure_replication_schedule

    Activities->>Client: Set Replication Schedule
    Client->>PrimarySite: PATCH /snapmirror/relationships/sm-rel-001
    Note right of Client: Schedule: Every 4 hours
    PrimarySite-->>Client: Schedule Configured

    Activities-->>Worker: Schedule Active

    Worker->>State: Update: schedule_configured
    Worker->>Activities: setup_monitoring_alerts

    Activities->>Client: Configure SnapMirror Alerts
    Client->>PrimarySite: POST /management-server/events/rules
    PrimarySite-->>Client: Alert Rules Created

    Activities->>Client: Configure Secondary Site Monitoring
    Client->>SecondarySite: POST /management-server/events/rules
    SecondarySite-->>Client: Alert Rules Created

    Worker->>State: Update: monitoring_configured
    Worker->>Activities: test_failover_capability

    Activities->>Client: Test Break and Resync
    Client->>SecondarySite: POST /snapmirror/relationships/sm-rel-001/break
    SecondarySite-->>Client: Break Successful

    Activities->>Client: Test Resync
    Client->>PrimarySite: POST /snapmirror/relationships/sm-rel-001/resync
    PrimarySite-->>Client: Resync Initiated

    Activities->>Monitor: Wait for Resync
    Monitor->>Client: Check Resync Status
    Client->>PrimarySite: GET /snapmirror/relationships/sm-rel-001
    PrimarySite-->>Client: Status: Snapmirrored
    Monitor-->>Activities: Failover Test Complete

    Worker->>State: Update: tested
    Worker->>Activities: generate_dr_documentation

    Activities->>Client: Generate DR Procedures
    Client-->>Activities: DR Documentation Created

    Worker->>State: Update: workflow_complete
    Worker-->>Temporal: Multi-Site Replication Complete

    Temporal-->>APIM: DR Replication configured successfully
    APIM-->>DevOps: DR Setup Complete
    Note right of DevOps: prod-vol-001 → dr-site, Schedule: 4hrs, Failover tested
```

## Component Interaction Patterns

### 1. Request Processing Pattern

```mermaid
graph LR
    A[CMP-0001<br/>AI Assistant<br/>Interface] -->|MCP Request| B[CMP-0002<br/>MCP Protocol<br/>Gateway]
    B -->|Route| C[CMP-0003<br/>Request<br/>Router]
    C -->|Validate| D[CMP-0004<br/>Schema<br/>Validator]
    C -->|Lookup| E[CMP-0005<br/>Tool<br/>Registry]
    C -->|Authenticate| F[CMP-0007<br/>Authentication<br/>Manager]
    C -->|Execute| G[CMP-0008<br/>NetApp API<br/>Client]
    G -->|Cache| H[CMP-0013<br/>Cache<br/>Manager]
    C -->|Format| I[CMP-0006<br/>Response<br/>Formatter]
    I -->|Response| B
    B -->|Result| A

    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style G fill:#fff3e0
    style H fill:#fce4ec
```

### 2. Workflow Orchestration Pattern

```mermaid
graph TD
    A[CMP-0001<br/>AI Assistant<br/>Interface] -->|Workflow Request| B[CMP-0009<br/>Temporal Workflow<br/>Engine]
    B -->|Assign| C[CMP-0011<br/>Temporal<br/>Workers]
    C -->|Execute| D[CMP-0010<br/>Workflow<br/>Activities]
    D -->|NetApp Call| E[CMP-0008<br/>NetApp API<br/>Client]
    E -->|API Request| F[CMP-0016<br/>NetApp<br/>Infrastructure]
    C -->|Persist State| G[CMP-0012<br/>Workflow State<br/>Store]
    B -->|Monitor| H[CMP-0018<br/>Monitoring<br/>Stack]
    F -->|Events| I[CMP-0014<br/>Event<br/>Processor]
    I -->|Trigger| B

    style A fill:#e1f5fe
    style B fill:#e8f5e8
    style C fill:#e8f5e8
    style D fill:#e8f5e8
    style E fill:#fff3e0
    style F fill:#ffebee
    style G fill:#f1f8e9
    style H fill:#fce4ec
    style I fill:#fff8e1
```

### 3. Event-Driven Pattern

```mermaid
graph LR
    A[CMP-0016<br/>NetApp<br/>Infrastructure] -->|Events| B[CMP-0014<br/>Event<br/>Processor]
    B -->|Process & Filter| C[CMP-0009<br/>Temporal Workflow<br/>Engine]
    C -->|Orchestrate| D[CMP-0011<br/>Temporal<br/>Workers]
    D -->|Execute Activities| E[CMP-0010<br/>Workflow<br/>Activities]
    E -->|NetApp Actions| F[CMP-0008<br/>NetApp API<br/>Client]
    F -->|API Calls| A

    style A fill:#ffebee
    style B fill:#fff8e1
    style C fill:#e8f5e8
    style D fill:#e8f5e8
    style E fill:#e8f5e8
    style F fill:#fff3e0
```

### 4. Cache-Enabled Request Pattern

```mermaid
graph TD
    A[CMP-0001<br/>AI Assistant<br/>Interface] -->|Query Request| B[CMP-0002<br/>MCP Protocol<br/>Gateway]
    B --> C[CMP-0003<br/>Request<br/>Router]
    C --> D[CMP-0013<br/>Cache<br/>Manager]

    D -->|Cache Hit| E[Cached Response]
    D -->|Cache Miss| F[CMP-0008<br/>NetApp API<br/>Client]

    F --> G[CMP-0016<br/>NetApp<br/>Infrastructure]
    G --> H[Fresh Data]
    H --> I[Update Cache]
    I --> J[Return Response]

    E --> K[Format Response]
    J --> K
    K --> B
    B --> A

    style A fill:#e1f5fe
    style D fill:#fce4ec
    style F fill:#fff3e0
    style G fill:#ffebee
```

### 5. Security Context Pattern

```mermaid
graph TD
    A[Incoming Request] --> B[CMP-0007<br/>Authentication<br/>Manager]
    B --> C[CMP-0015<br/>Security<br/>Context]
    C --> D{Credentials<br/>Valid?}

    D -->|Yes| E[CMP-0008<br/>NetApp API<br/>Client]
    D -->|No| F[Access Denied]

    E --> G[Encrypted Channel]
    G --> H[CMP-0016<br/>NetApp<br/>Infrastructure]

    C --> I[CMP-0019<br/>Configuration<br/>Manager]
    I --> J[Environment<br/>Configs]

    style B fill:#ffcdd2
    style C fill:#ffcdd2
    style E fill:#fff3e0
    style G fill:#e8f5e8
    style H fill:#ffebee
    style I fill:#f3e5f5
```

### 6. Health Monitoring Pattern

```mermaid
graph LR
    A[CMP-0020<br/>Health<br/>Monitor] -->|Check| B[CMP-0008<br/>NetApp API<br/>Client]
    A -->|Check| C[CMP-0009<br/>Temporal Workflow<br/>Engine]
    A -->|Check| D[CMP-0013<br/>Cache<br/>Manager]
    A -->|Check| E[CMP-0012<br/>Workflow State<br/>Store]

    B -->|Status| F[Health Report]
    C -->|Status| F
    D -->|Status| F
    E -->|Status| F

    F --> G[CMP-0018<br/>Monitoring<br/>Stack]
    G --> H[Alerts &<br/>Dashboards]

    style A fill:#e3f2fd
    style F fill:#e3f2fd
    style G fill:#fce4ec
    style H fill:#fce4ec
```

## Technical Specifications

### Component Specifications

#### CMP-0009: Temporal Workflow Engine

**Configuration:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: temporal-server
  labels:
    component: CMP-0009
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: temporal-server
        image: temporalio/auto-setup:1.20.0
        ports:
        - containerPort: 7233
          name: grpc
        - containerPort: 8080
          name: web
        env:
        - name: DB
          value: postgresql
        - name: POSTGRES_SEEDS
          value: postgres-cluster:5432
        - name: DYNAMIC_CONFIG_FILE_PATH
          value: /etc/temporal/config/dynamicconfig.yaml
        resources:
          requests:
            memory: 1Gi
            cpu: 500m
          limits:
            memory: 2Gi
            cpu: 1000m
```

**Interfaces:**
- **gRPC API**: Port 7233 for workflow and activity communication
- **Web UI**: Port 8080 for workflow monitoring and debugging
- **Database**: PostgreSQL for state persistence

#### CMP-0008: NetApp API Client

**Configuration:**
```python
class NetAppAPIClient:
    def __init__(self, config: NetAppConfig):
        self.base_url = f"https://{config.host}/api/v2"
        self.session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(config.username, config.password),
            connector=aiohttp.TCPConnector(
                ssl=False if not config.verify_ssl else None,
                limit=20,
                limit_per_host=10,
                keepalive_timeout=30
            ),
            timeout=aiohttp.ClientTimeout(total=config.timeout)
        )

    async def make_request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with self.session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
```

**API Endpoints Supported:**
- Administration: `/admin/*`
- Datacenter: `/datacenter/*`
- Storage Provider: `/storage-provider/*`
- Management Server: `/management-server/*`
- Gateways: `/gateways/*`

### Performance Specifications

| **Component** | **Throughput** | **Latency** | **Scalability** | **Resource Requirements** |
|---------------|----------------|-------------|-----------------|--------------------------|
| **CMP-0002** | 1000 req/sec | <10ms | Horizontal (Knative) | 256Mi RAM, 200m CPU |
| **CMP-0008** | 500 req/sec | <100ms | Connection pooling | 512Mi RAM, 500m CPU |
| **CMP-0009** | 10000 workflows/sec | <50ms | Cluster-wide | 2Gi RAM, 1 CPU |
| **CMP-0011** | 1000 activities/sec | Variable | Worker scaling | 1Gi RAM, 500m CPU |
| **CMP-0013** | 5000 ops/sec | <5ms | Redis cluster | 1Gi RAM, 200m CPU |

### Security Specifications

#### Authentication and Authorization

```yaml
# CMP-0015: Security Context Configuration
apiVersion: v1
kind: Secret
metadata:
  name: netapp-credentials
  namespace: netapp-mcp
type: Opaque
data:
  endpoint: <base64-encoded-url>
  username: <base64-encoded-username>
  password: <base64-encoded-password>
  ca-cert: <base64-encoded-ca-certificate>

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: netapp-mcp-service
  namespace: netapp-mcp
  annotations:
    component: CMP-0007

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: netapp-mcp
  name: netapp-mcp-role
rules:
- apiGroups: [""]
  resources: ["secrets", "configmaps"]
  verbs: ["get", "list"]
- apiGroups: ["serving.knative.dev"]
  resources: ["services"]
  verbs: ["get", "list", "patch"]
```

#### Network Security

```yaml
# Network Policy for Component Isolation
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: netapp-mcp-network-policy
  namespace: netapp-mcp
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/part-of: netapp-mcp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: knative-serving
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # NetApp HTTPS
    - protocol: TCP
      port: 7233 # Temporal gRPC
    - protocol: TCP
      port: 5432 # PostgreSQL
    - protocol: TCP
      port: 6379 # Redis
```

## Monitoring and Observability

### Metrics Collection

```yaml
# CMP-0018: Monitoring Stack Configuration
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: netapp-mcp-components
  namespace: netapp-mcp
spec:
  selector:
    matchLabels:
      app.kubernetes.io/part-of: netapp-mcp
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
    scrapeTimeout: 10s
```

### Key Metrics

| **Component** | **Metric Name** | **Type** | **Purpose** |
|---------------|-----------------|----------|-------------|
| **CMP-0002** | `mcp_requests_total` | Counter | Track request volume |
| **CMP-0008** | `netapp_api_calls_total` | Counter | Monitor API usage |
| **CMP-0009** | `temporal_workflow_executions_total` | Counter | Workflow tracking |
| **CMP-0011** | `temporal_activity_executions_total` | Counter | Activity monitoring |
| **CMP-0013** | `cache_operations_total` | Counter | Cache performance |
| **CMP-0020** | `health_check_status` | Gauge | System health |

### Distributed Tracing

```python
# OpenTelemetry Integration
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracing for all components
tracer_provider = TracerProvider()
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-agent",
    agent_port=6831
)
span_processor = BatchSpanProcessor(jaeger_exporter)
tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)

# Component-specific tracers
cmp_0002_tracer = trace.get_tracer("CMP-0002-MCP-Gateway")
cmp_0008_tracer = trace.get_tracer("CMP-0008-NetApp-Client")
cmp_0009_tracer = trace.get_tracer("CMP-0009-Temporal-Engine")
```

This comprehensive technical documentation provides detailed component models, sequence diagrams, and specifications for implementing and operating the NetApp ActiveIQ MCP Server with Temporal.io integration.
