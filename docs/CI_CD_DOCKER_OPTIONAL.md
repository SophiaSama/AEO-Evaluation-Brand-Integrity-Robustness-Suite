# Docker Support for BIRS CI/CD (Optional)

## Current Status: Docker NOT Required ✅

All BIRS CI/CD workflows run on **GitHub-hosted Ubuntu VMs** without Docker. This is the recommended approach because it's:
- ✅ Faster (no image pulling)
- ✅ Simpler (less configuration)
- ✅ Well-cached (pip cache works natively)
- ✅ Free (included in GitHub Actions)

## When You Might Want Docker

Consider using Docker if you need:

1. **Reproducible environments** across local dev and CI
2. **Complex dependencies** that are hard to install
3. **Multiple services** (databases, message queues, etc.)
4. **Specific OS/version requirements** not available in GitHub runners

---

## Option 1: Run Jobs in Containers

You can run individual jobs inside Docker containers:

```yaml
# Example: ci-tests-docker.yml
name: BIRS CI Tests (Docker)

on:
  push:
    branches: [main]

jobs:
  test-in-container:
    runs-on: ubuntu-latest
    container:
      image: python:3.11-slim
      options: --cpus 2 --memory 4g
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install dependencies
        run: |
          pip install --no-cache-dir -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest tests/ -v
```

**Pros:**
- Guaranteed consistent Python version
- Isolated environment
- Can use custom base images

**Cons:**
- Slower startup (image pull)
- Some actions may not work in containers
- More complex debugging

---

## Option 2: Use Docker Compose for Services

Run ChromaDB and other services in Docker:

```yaml
# Example: ci-integration-docker.yml
name: BIRS Integration (with Docker Compose)

on:
  push:
    branches: [main]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Start services with Docker Compose
        run: |
          docker-compose up -d chromadb ollama
          docker-compose ps
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Wait for services
        run: |
          timeout 60 bash -c 'until docker-compose exec -T chromadb curl -f http://localhost:8000/api/v1/heartbeat; do sleep 2; done'
      
      - name: Run integration tests
        run: pytest tests/ -m integration
      
      - name: Stop services
        if: always()
        run: docker-compose down -v
```

**Requires:** `docker-compose.yml` in your repo:

```yaml
# docker-compose.yml
version: '3.8'

services:
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma-data:/chroma/chroma
    environment:
      - ALLOW_RESET=true
  
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama

volumes:
  chroma-data:
  ollama-data:
```

---

## Option 3: Build Custom Docker Image

Create a Dockerfile for BIRS:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command
CMD ["python", "-m", "pytest", "tests/"]
```

**Build and push:**
```bash
docker build -t ghcr.io/<username>/birs:latest .
docker push ghcr.io/<username>/birs:latest
```

**Use in workflow:**
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/<username>/birs:latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest tests/
```

---

## Option 4: Matrix Testing with Multiple Images

Test against different Python versions using containers:

```yaml
name: Matrix Docker Tests

on: [push]

jobs:
  test-matrix:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-image:
          - python:3.10-slim
          - python:3.11-slim
          - python:3.12-slim
    
    container:
      image: ${{ matrix.python-image }}
    
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: pytest tests/
```

---

## Hybrid Approach (Recommended if Using Docker)

Use Docker for services, native Python for tests:

```yaml
name: Hybrid Approach

on: [push]

jobs:
  test-with-services:
    runs-on: ubuntu-latest
    
    services:
      chromadb:
        image: chromadb/chroma:latest
        ports:
          - 8000:8000
        options: >-
          --health-cmd "curl -f http://localhost:8000/api/v1/heartbeat || exit 1"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests with ChromaDB service
        run: pytest tests/ -m integration
        env:
          CHROMADB_HOST: localhost
          CHROMADB_PORT: 8000
```

**Pros:**
- Services in containers (isolated)
- Tests run on VM (fast, well-cached)
- Best of both worlds

---

## Performance Comparison

| Approach | Startup Time | Caching | Complexity |
|----------|--------------|---------|------------|
| **Native VM (current)** | ~30s | ✅ Excellent | ⭐ Low |
| **Job in container** | ~60s | ⚠️ Good | ⭐⭐ Medium |
| **Docker Compose** | ~90s | ⚠️ Good | ⭐⭐⭐ High |
| **Custom image** | ~45s | ✅ Excellent | ⭐⭐⭐ High |
| **Hybrid (services)** | ~40s | ✅ Excellent | ⭐⭐ Medium |

---

## Recommendation

### For BIRS: Stick with Current Approach ✅

**Why:**
- BIRS doesn't need complex service orchestration
- Ollama installs easily via shell script
- ChromaDB runs in-process (embedded mode)
- Native Python is faster and simpler
- GitHub-hosted runners are well-maintained

### Consider Docker if:
- You need to test against external databases
- You want identical local and CI environments
- You're deploying BIRS as a containerized service
- You need specific system dependencies

---

## Migration Guide (If You Want Docker)

### Step 1: Create Dockerfile
```bash
# Create Dockerfile in repo root
code Dockerfile
```

### Step 2: Test Locally
```bash
docker build -t birs-local .
docker run -it birs-local pytest tests/
```

### Step 3: Update Workflow
```yaml
# Choose one of the options above
# Test in a feature branch first
```

### Step 4: Push to Registry (Optional)
```bash
# If using custom image
docker tag birs-local ghcr.io/${{ github.repository }}:latest
docker push ghcr.io/${{ github.repository }}:latest
```

---

## Troubleshooting Docker in GitHub Actions

### Issue: Image pull timeout
```yaml
# Increase timeout
jobs:
  test:
    timeout-minutes: 30  # Default is 360
```

### Issue: Actions don't work in containers
```yaml
# Use docker-inside-docker approach
- uses: actions/checkout@v4
  with:
    persist-credentials: true  # May be needed
```

### Issue: Volume permissions
```yaml
container:
  image: python:3.11
  options: --user root  # Run as root if needed
```

---

## Conclusion

**Docker is NOT required for BIRS CI/CD.** The current implementation using native GitHub runners is:
- ✅ Faster
- ✅ Simpler
- ✅ Better cached
- ✅ Recommended for most Python projects

**Use Docker only if** you have specific requirements that GitHub's native runners can't handle.

---

*Last updated: February 6, 2026*
