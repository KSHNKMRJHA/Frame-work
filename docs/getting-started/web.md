# Web Deployment

Deploy FrameWork to the cloud — Streamlit Community Cloud, Render, Railway, Fly.io, or Docker.

## Option 1: Streamlit Community Cloud (Easiest, Free for Public Repos)

1. Push your fork to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app**
4. Select your repo, branch `main`, entry point `app.py`
5. Deploy — auto-updates on every push

### Configuration

Create `.streamlit/config.toml` in your repo (already included):

```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = true
port = 8501

[theme]
base = "light"
primaryColor = "#4f46e5"
```

### Secrets

For private config (API keys, etc.), use Streamlit Cloud **Secrets** dashboard:

```toml
# .streamlit/secrets.toml (local only, not committed)
FRAMEWORK_WEB_URL = "https://your-custom-domain.com"
```

Access in code: `st.secrets["FRAMEWORK_WEB_URL"]`

---

## Option 2: Render

### render.yaml

```yaml
services:
  - type: web
    name: framework
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

Deploy: Connect repo at [dashboard.render.com](https://dashboard.render.com)

---

## Option 3: Railway

```bash
# Install CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### railway.toml

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"
healthcheckPath = "/"
healthcheckTimeout = 100
```

---

## Option 4: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Launch
fly launch --name framework-app --region ord --no-deploy
fly deploy
```

### fly.toml

```toml
app = "framework-app"
primary_region = "ord"

[build]
  [build.args]
    PYTHON_VERSION = "3.11"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

### Dockerfile for Fly.io

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system deps for matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true"]
```

---

## Option 5: Docker (Any Host)

### Dockerfile

```dockerfile
# Multi-stage for smaller image
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Runtime deps for matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

### Build & Run

```bash
docker build -t framework .
docker run -p 8501:8501 framework
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  framework:
    build: .
    ports:
      - "8501:8501"
    environment:
      - FRAMEWORK_WEB_URL=https://your-domain.com
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## Option 6: Kubernetes

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: framework
spec:
  replicas: 2
  selector:
    matchLabels:
      app: framework
  template:
    metadata:
      labels:
        app: framework
    spec:
      containers:
      - name: framework
        image: your-registry/framework:latest
        ports:
        - containerPort: 8501
        env:
        - name: FRAMEWORK_WEB_URL
          value: "https://framework.your-domain.com"
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: framework
spec:
  selector:
    app: framework
  ports:
  - port: 80
    targetPort: 8501
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: framework
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - framework.your-domain.com
    secretName: framework-tls
  rules:
  - host: framework.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: framework
            port:
              number: 80
```

---

## Environment Variables for Web

| Variable | Description | Required |
|----------|-------------|----------|
| `FRAMEWORK_WEB_URL` | Canonical URL for footer/links | No |
| `FRAMEWORK_BUILD_CHANNEL` | Release channel label | No (default: `stable`) |
| `FRAMEWORK_BUILD_COMMIT` | Override commit hash | No (auto from git) |

---

## Health Checks

All platforms should use Streamlit's built-in health endpoint:

```
GET /_stcore/health
```

Returns `200 OK` when the server is ready.

---

## Custom Domain

1. Add CNAME record: `framework.your-domain.com` → `<platform>.app` (or load balancer)
2. Configure TLS (auto via Let's Encrypt on most platforms)
3. Set `FRAMEWORK_WEB_URL=https://framework.your-domain.com`

---

## Next Steps

- [Desktop Build](desktop.md) — Standalone executable
- [Mobile (Android)](mobile.md) — APK build
- [CI/CD](../development/ci-cd.md) — Automated deployment