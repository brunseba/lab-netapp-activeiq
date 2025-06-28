# Target Operating Model: OpenFaaS MCP Server Deployment

## Overview

This Target Operating Model (TOM) outlines the deployment of a Model Context Protocol (MCP) server using OpenFaaS. OpenFaaS provides a serverless framework to package server functionalities as containerized functions, enabling convenient deployment and autoscaling on Kubernetes, OpenShift, or a standalone server.

## Executive Summary

Deploying MCP server operations with OpenFaaS ensures:
- **Scalability**: Dynamic autoscaling based on demand
- **Operational Efficiency**: Lower overhead by utilizing serverless container functions
- **Flexibility**: Support for any language, provided in a container
- **Ease of Management**: Web-based and CLI management tools

## Function Preparation and Deployment

### Step-by-Step Deployment

#### 1. Prepare MCP Server Code
- Ready your MCP server executable code.
- Use a command such as:
  ```
  npx -y @modelcontextprotocol/server-filesystem /data
  ```

#### 2. Scaffold an OpenFaaS Function
- Initialize your project:
  ```
  faas-cli new mcp-server --lang dockerfile
  ```
- This command will structure your function directory with Dockerfile support.

#### 3. Customize Dockerfile
- Edit the Dockerfile to install dependencies and set the execution command:
  ```Dockerfile
  FROM node:20-alpine

  WORKDIR /app
  RUN npm install -g @modelcontextprotocol/server-filesystem

  COPY handler.sh .
  RUN chmod +x handler.sh

  ENV fprocess="npx -y @modelcontextprotocol/server-filesystem /data"
  CMD ["fwatchdog"]
  ```
- `handler.sh` facilitates additional custom execution if needed, controlled by the `fprocess` environment.

#### 4. Setup OpenFaaS Function Configuration
- Configure `mcp-server.yml`:
  ```yaml
  provider:
    name: openfaas
    gateway: http://127.0.0.1:8080

  functions:
    mcp-server:
      lang: dockerfile
      handler: ./mcp-server
      image: your_dockerhub_username/mcp-server:latest
  ```
- Update with your Docker Hub credentials.

#### 5. Build and Deploy
- Build and push the Docker image:
  ```
  faas-cli build -f mcp-server.yml
  faas-cli push -f mcp-server.yml
  ```
- Deploy your function to the OpenFaaS gateway:
  ```
  faas-cli deploy -f mcp-server.yml
  ```

#### 6. Confirm and Test
- Confirm deployment:
  ```
  faas-cli list
  ```
- Invoke the function:
  ```
  echo "test" | faas-cli invoke mcp-server
  ```

## Architectural Benefits

### Function Management
- **Easy Scaling**: Functions scale automatically based on demand
- **Efficient Resource Allocation**: Only utilize resources during active requests

### Development and Operations
- **Language Agnostic**: Supported deployment of any language as long as it fits within a container
- **Robust Tooling**: OpenFaaS CLI and UI simplify function management

## Key Notes
- The `fprocess` environment variable defines function execution. It tailors the OpenFaaS handling process uniquely for any MCP node command.
- OpenFaaS supports a multi-cloud setup, offering flexibility in hosting serverless functions across varied infrastructures.

## Business Impact

**Enhanced Flexibility**: Allows deploying serverless MCP instances at scale with lower costs and enhanced manageability.

**Improved Resource Utilization**: Ensures optimal cost savings by running functions only when needed, reducing idle time to zero.

Deploying an MCP server as an OpenFaaS function provides a modern, cloud-native approach to dynamic serverless deployments, fully leveraging OpenFaaS's robust features for maximum efficiency and ease of operation.

