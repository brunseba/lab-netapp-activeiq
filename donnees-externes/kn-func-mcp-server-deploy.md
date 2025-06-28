## Knative Function Usage for Deploying an MCP Server from Code

Deploying an MCP (Model Context Protocol) server as a Knative function involves packaging your server code as a container image and deploying it as a Knative Service, enabling autoscaling and serverless capabilities. Below is a step-by-step guide to achieve this, referencing Knative function usage and specifics for MCP server deployment.

**1. Prepare Your MCP Server Code**

- Ensure your MCP server code is ready and can be run as a containerized application.
- For example, you might use a command like:
  ```
  npx -y @modelcontextprotocol/server-filesystem /data
  ```
  as the entry point for your server[1].

**2. Initialize a Knative Function Project (Optional)**

- If you want to use the Knative Functions CLI (`kn func`), initialize your function project:
  ```
  kn func create <project-name> --runtime <runtime>
  ```
- Place your MCP server code in this project directory.

**3. Build and Deploy the Function**

- Use the Knative Functions CLI to build and deploy your function as a Knative Service:
  ```
  kn func deploy --registry <your-registry>
  ```
  This command will:
  - Build the function into a container image.
  - Push the image to your specified container registry.
  - Deploy the image as a Knative Service on your cluster[2][3].

- If you already have a Dockerfile and want to deploy directly from source (e.g., using Kaniko or Ko for Go projects), you can set up a YAML manifest that references your Git repo and build instructions[4].

**4. Define the Knative Service (YAML Example)**

You can manually define a Knative Service manifest for your MCP server. Here is an example adapted for an MCP server using IBM Cloud Code Engine, but this pattern works for any Knative Serving setup:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
meta
  name: mcp-server-filesystem
spec:
  template:
    meta
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/scale-down-delay: "0"
        autoscaling.knative.dev/target: "100"
    spec:
      containerConcurrency: 100
      containers:
        - args:
            - --stdio
            - "npx -y @modelcontextprotocol/server-filesystem /data"
            - --outputTransport
            - sse
```
- This manifest sets up autoscaling and concurrency, and runs your MCP server with the specified arguments[1].

Deploy this manifest with:
```
kubectl apply -f <your-manifest>.yaml
```

**5. Access and Test the Service**

- Once deployed, Knative exposes your service with an HTTP endpoint.
- You can retrieve the service URL using:
  ```
  kubectl get ksvc mcp-server-filesystem
  ```
- Or, if using a managed Knative environment, the endpoint may be provided directly.

**6. Advanced: Deploy Directly from Source (Optional)**

- For Go-based MCP servers, you can use `ko` to build and deploy directly from source without a Dockerfile[4].
- For other languages, you can use Kaniko in-cluster builds, referencing your Git repo and Dockerfile in the Knative Service manifest[4].

## Summary Table: Knative Function CLI vs. Manual YAML

| Method                  | Build & Deploy Command                                 | Source Format         | Registry Needed | Example Use Case            |
|-------------------------|--------------------------------------------------------|-----------------------|-----------------|-----------------------------|
| Knative Functions CLI   | `kn func deploy --registry <registry>`                 | Local project         | Yes             | Quick local development     |
| Manual YAML             | `kubectl apply -f <manifest>.yaml`                    | Container image       | Yes             | Custom configuration        |
| Kaniko/Ko (from source) | `kubectl apply -f <manifest>.yaml` (with build spec)   | Git repo (source)     | Yes             | CI/CD pipelines, Go apps    |

## Key Points

- Use `kn func deploy` for streamlined function deployment from local code[2][3].
- For more control, define a Knative Service YAML manifest referencing your MCP server image and arguments[1].
- Both approaches require a container registry.
- Knative provides autoscaling, concurrency controls, and scale-to-zero features out of the box[5].

This workflow enables you to deploy an MCP server as a serverless function on Kubernetes using Knative, leveraging modern cloud-native patterns for scalability and efficiency.

Sources
[1] Deploying your MCP server on IBM Cloud Code Engine https://community.ibm.com/community/user/blogs/jeremias-werner/2025/04/30/code-engine-mcp-server
[2] Deploying functions - Knative https://knative.dev/docs/functions/deploying-functions/
[3] Chapter 5. Knative Functions CLI commands - Red Hat Documentation https://docs.redhat.com/en/documentation/red_hat_openshift_serverless/1.29/html/knative_cli/knative-functions-cli-commands
[4] Deploy Knative Service directly from source code using Kaniko / Ko https://blog.francium.tech/deploy-knative-service-directly-from-source-code-using-kaniko-ko-62f628a010d2
[5] Turn a Kubernetes deployment into a Knative service - Red Hat https://www.redhat.com/en/blog/kubernetes-deployment-knative-service
[6] Deploying a Knative Service https://knative.dev/docs/getting-started/first-service/
[7] Knative : fonctions et événements sur Kubernetes - Blog Ippon https://blog.ippon.fr/2024/01/24/knative-executez-vos-fonctions-et-adoptez-une-architecture-evenementielle-sur-kubernetes/
[8] How to Build an MCP Server (Step-by-Step Guide) 2025 - Leanware https://www.leanware.co/insights/how-to-build-mcp-server
[9] Knative Serving code samples https://knative.dev/docs/samples/serving/
[10] Knative: Functions AI Agent Callbacks - Google Summer of Code https://summerofcode.withgoogle.com/programs/2025/projects/llt9vHfu
[11] Building, running, or deploying a function - Knative https://knative.dev/docs/getting-started/build-run-deploy-func/
[12] Container Service for Kubernetes:Deploy Knative Functions https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/creating-knative-based-functions-with-knative-functions
[13] Using Knative and Ambassador Edge Stack to Handle Traffic https://blog.getambassador.io/using-knative-and-ambassador-edge-stack-to-handle-traffic-5b938470d51f
[14] What's the best way to deploy an Model Context Protocol (MCP ... https://milvus.io/ai-quick-reference/whats-the-best-way-to-deploy-an-model-context-protocol-mcp-server-to-production
[15] Knative Eventing Hello World: An Introduction to Knative https://www.alibabacloud.com/blog/knative-eventing-hello-world-an-introduction-to-knative_595789
[16] Deploy a serverless workload on Kubernetes using Knative and ... https://circleci.com/blog/deploy-serverless-workload-with-knative/

