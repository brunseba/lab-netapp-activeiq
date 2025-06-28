## Deploying an MCP Server as an OpenFaaS Function

To deploy an MCP (Model Context Protocol) server using OpenFaaS, you’ll package your server as a Docker image and expose it as a function. OpenFaaS runs on Kubernetes, K3s, OpenShift, or even a single host, and provides both CLI and web UI for deployment[1][2][3].

**Step-by-Step Guide**

**1. Prepare Your MCP Server Code**

- Ensure your MCP server code can be started with a command such as:
  ```
  npx -y @modelcontextprotocol/server-filesystem /data
  ```
- Place your code in a directory suitable for containerization.

**2. Scaffold an OpenFaaS Function**

- Use the OpenFaaS CLI to scaffold a new function project. For a generic container (custom Dockerfile), run:
  ```
  faas-cli new mcp-server --lang dockerfile
  ```
- This creates a directory `mcp-server` with a basic `Dockerfile` and handler.

**3. Customize the Dockerfile**

- Edit the `Dockerfile` to install your dependencies and set the correct entrypoint. For example:
  ```Dockerfile
  FROM node:20-alpine

  WORKDIR /app
  RUN npm install -g @modelcontextprotocol/server-filesystem

  COPY handler.sh .
  RUN chmod +x handler.sh

  ENV fprocess="npx -y @modelcontextprotocol/server-filesystem /data"
  CMD ["fwatchdog"]
  ```

- In `handler.sh`, you can leave it empty or use as needed, since the main process is handled by `fprocess`.

**4. Define the Function in YAML**

- Edit the `mcp-server.yml` (or `stack.yml`) file to look like:
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
- Replace `your_dockerhub_username` with your Docker Hub username.

**5. Build and Push the Docker Image**

- Run the following commands to build and push your function:
  ```
  faas-cli build -f mcp-server.yml
  faas-cli push -f mcp-server.yml
  ```
  This builds the Docker image and pushes it to Docker Hub[3][4].

**6. Deploy the Function to OpenFaaS**

- Deploy your function to the OpenFaaS gateway:
  ```
  faas-cli deploy -f mcp-server.yml
  ```
- Confirm deployment:
  ```
  faas-cli list
  ```
  This will show your function as deployed and ready to invoke[2][3][4].

**7. Test Your MCP Server Function**

- Invoke the function via CLI:
  ```
  echo "test" | faas-cli invoke mcp-server
  ```
- Or, use the web UI at `http://<gateway-address>:8080`, find your function, and invoke it from the browser[2][3].

**Key Notes**

- OpenFaaS uses the `fprocess` environment variable to specify the command your function runs. For an MCP server, this is typically your node command.
- The function auto-scales based on requests, and can be managed via CLI or web UI[2].
- You can use any language or base image, as long as your server runs as a process that reads from `stdin` and writes to `stdout`.

This approach provides a repeatable, containerized, serverless deployment of your MCP server using OpenFaaS, leveraging its autoscaling and management features[2][3][4].

Sources
[1] Deployment overview - OpenFaaS https://docs.openfaas.com/deployment/
[2] Create Serverless Functions with OpenFaaS - Gcore https://gcore.com/learning/create-serverless-functions-with-openfaas
[3] How To Run Serverless Functions Using OpenFaaS ... - DigitalOcean https://www.digitalocean.com/community/tutorials/how-to-run-serverless-functions-using-openfaas-on-digitalocean-kubernetes
[4] OpenFaaS Tutorial: Build and Deploy Serverless Java Functions https://www.upnxtblog.com/index.php/2018/10/19/openfaas-tutorial-build-and-deploy-serverless-java-functions/
[5] First Python Function - OpenFaaS https://docs.openfaas.com/tutorials/first-python-function/
[6] Here's an MCP server that can list and invoke functions in… | Alex Ellis https://www.linkedin.com/posts/alexellisuk_heres-an-mcp-server-that-can-list-and-invoke-activity-7317479827773542400-f9Th
[7] Deploy your first Serverless Function to Kubernetes - ITNEXT https://itnext.io/deploy-your-first-serverless-function-to-kubernetes-232307f7b0a9
[8] How to Build & Integrate with Functions using OpenFaaS https://www.openfaas.com/blog/integrate-with-openfaas/
[9] Serverless with OpenFaaS and .NET | by Goncalo Oliveira | ITNEXT https://itnext.io/serverless-with-openfaas-and-net-6a66b5c30a5f
[10] Demystifying Serverless & OpenFaas - Collabnix https://collabnix.com/demystifying-openfaas-simplifying-serverless-computing/
[11] Self Hosted Serverless Functions with OpenFaaS and Kubernetes https://docs.vultr.com/self-hosted-serverless-functions-with-openfaas-and-kubernetes
[12] How to build functions from source code with the Function Builder API https://www.openfaas.com/blog/how-to-build-via-api/
[13] How to Create Serverless Functions with OpenFaaS in 17 Steps https://hackernoon.com/how-to-create-serverless-functions-with-openfaas-in-17-steps-u21l3y7m
[14] Build Remote MCP servers using Azure Functions in TypeScript https://www.youtube.com/watch?v=U9DsLcP5vEk

