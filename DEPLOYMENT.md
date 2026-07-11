# AutoOps Deployment & Integration Guide

This guide details how to deploy and integrate **AutoOps** into environments where application services and telemetry infrastructure (Prometheus, Grafana Loki, Jaeger) are already running.

---

## Architecture Overview

AutoOps runs as a two-tier containerized stack:
1. **Frontend (Nginx)**: Serves the compiled React UI and acts as a reverse proxy routing `/api` and `/webhook` calls to the backend.
2. **Backend (FastAPI & LangGraph)**: Executes telemetry collection, log correlation, trace-span parsing, and calls the LiteLLM/Gemini reasoning engine.

```
                  ┌──────────────────────────────────────────────┐
                  │                 Docker Host                  │
                  │                                              │
                  │   ┌──────────────────────────────────────┐   │
                  │   │             AutoOps Stack            │   │
  User Browser ───┼──►│  frontend (Nginx Proxy)  [:8080]     │   │
                  │   └───┬──────────────────────────┬───────┘   │
                  │       │ /api                     │ /webhook  │
                  │   ┌───▼──────────────────────────▼───────┐   │
                  │   │       backend (FastAPI)      [:8000] │   │
                  │   └───┬──────────────┬───────────┬───────┘   │
                  │       │ PromQL       │ LogQL     │ Traces    │
                  │   ┌───▼──────────┐ ┌─▼─────────┐ ┌─▼───────┐ │
                  │   │  Prometheus  │ │GrafanaLoki│ │ Jaeger  │ │
                  │   └──────────────┘ └───────────┘ └─────────┘ │
                  │     (Existing Telemetry Stack Containers)    │
                  └──────────────────────────────────────────────┘
```

---

## Prerequisites

Before deploying, ensure you have:
* **Docker & Docker Compose** installed.
* An active **Gemini API Key** (or another supported LiteLLM model provider key).
* Telemetry endpoints reachable from the Docker network:
  * **Prometheus** (Query API endpoint)
  * **Grafana Loki** (Query Range API endpoint)
  * **Jaeger** (JSON Traces API endpoint)

---

## Step 1: Copy Deployment Configurations

If you are deploying to a production or staging host, you do not need the full repository source code. You only need the deployment template files.

Copy `docker-compose.yml` and `.env.example` into a directory on the target server:

```bash
mkdir autoops-deploy && cd autoops-deploy
# Copy docker-compose.yml and .env.example into this directory
```

---

## Step 2: Environment Settings (`.env`)

Create your active configuration file by copying the template:

```bash
cp .env.example .env
```

Open `.env` and fill in the parameters:

```env
# LiteLLM/Gemini Setup
GEMINI_API_KEY=AIzaSyD...your_actual_api_key...
LITELLM_MODEL=gemini/gemini-2.5-flash

# Telemetry Endpoint Configurations (Select one of the Network Integration Scenarios below)
PROMETHEUS_URL=http://<host_or_container_name>:9090
LOKI_URL=http://<host_or_container_name>:3100
JAEGER_URL=http://<host_or_container_name>:16686
```

---

## Step 3: Network Integration Scenarios

Configure the URLs in `.env` based on how your telemetry services are hosted relative to the AutoOps containers.

### Scenario A: Telemetry is inside the same Docker Compose file
If you appended AutoOps services directly into your existing `docker-compose.yml` stack, they share a network. Use the container **service names** as hostnames:

```env
PROMETHEUS_URL=http://prometheus:9090
LOKI_URL=http://loki:3100
JAEGER_URL=http://jaeger:16686
```

### Scenario B: Telemetry is in a separate Compose stack (but same Host VM)
If your existing telemetry stack runs in a separate compose configuration on the same host, you can link the networks.

1. Find the name of your telemetry network:
   ```bash
   docker network ls
   ```
   *(e.g., `monitoring_default`)*
2. Update the network block at the bottom of your `docker-compose.yml`:
   ```yaml
   networks:
     default:
       name: monitoring_default
       external: true
   ```
3. Use the container service names in `.env` just like Scenario A.

### Scenario C: Telemetry is hosted on the host machine OS (Outside Docker)
If Prometheus, Loki, or Jaeger are running directly on the host machine (not in Docker), containers can reach them using the Docker host loopback IP gateway.

Keep the default `extra_hosts` configuration in `docker-compose.yml` and use `host.docker.internal` as the endpoint target:

```env
PROMETHEUS_URL=http://host.docker.internal:9090
LOKI_URL=http://host.docker.internal:3100
JAEGER_URL=http://host.docker.internal:16686
```

---

## Step 4: Start AutoOps

Launch the application stack using Docker Compose:

```bash
# If using pre-built images, replace build: block with image: in docker-compose.yml
# To run using local source files:
docker compose up -d --build
```

Verify that the services are up and healthy:

```bash
docker compose ps
```

The web console will be accessible on your browser at:
`http://<server-ip>:8080`

---

## Step 5: Route Alertmanager Alerts to AutoOps

To automate incident troubleshooting, integrate AutoOps with your Prometheus Alertmanager.

Update your `alertmanager.yml` configuration to include AutoOps as a webhook receiver:

```yaml
route:
  group_by: ['alertname', 'service', 'app']
  receiver: 'autoops-webhook'

receivers:
- name: 'autoops-webhook'
  webhook_configs:
  - url: 'http://<autoops-host-ip>:8080/webhook'
    send_resolved: true
```

Reload or restart your Alertmanager configuration to apply the receiver route.

---

## Troubleshooting

### Container Network Resolution Fails
If AutoOps fails to connect to Prometheus or Loki and shows errors in the logs:
* Check network reachability from inside the backend container:
  ```bash
  docker compose exec backend curl -v http://prometheus:9090/status
  ```
* Ensure ports `9090`, `3100`, and `16686` are exposed or bound correctly.

### Database Persistence
Incident investigation records are stored in an SQLite database. The database file is located inside the `backend-data` volume mapping at `/app/data/autoops.db`. 
Do not delete this volume unless you want to wipe all past incident histories.
