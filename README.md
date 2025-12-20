# Six Figure RAG - Server Setup Guide 🚀

A production-ready **Retrieval-Augmented Generation (RAG)** API built with FastAPI, featuring hybrid search, multi-query retrieval, and multi-modal document processing.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Step 1: Install WSL2](#step-1-install-wsl2)
- [Step 2: Install Docker Desktop](#step-2-install-docker-desktop)
- [Step 3: Setup Project](#step-3-setup-project)
- [Step 4: Install UV](#step-4-install-uv-python-package-manager)
- [Step 5: Install Supabase CLI](#step-5-install-supabase-cli)
- [Step 6: Configure Environment](#step-6-configure-environment)
- [Step 7: Start Supabase](#step-7-start-supabase)
- [Step 8: Run the Application](#step-8-run-the-application)
- [Step 9: Verify Setup](#step-9-verify-setup)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Common Issues & Fixes](#common-issues--fixes)
- [Useful Commands](#useful-commands)

---

## Prerequisites

Before starting, ensure you have:

| Software | Version | Download |
|----------|---------|----------|
| Windows | 10/11 (64-bit) | - |
| WSL2 | Latest | Built-in |
| Docker Desktop | Latest | [docker.com](https://www.docker.com/products/docker-desktop/) |
| Git | Latest | Included in WSL |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| UV | Latest | [astral.sh/uv](https://astral.sh/uv) |

---

## Step 1: Install WSL2

### 1.1 Open PowerShell as Administrator

```powershell
# Install WSL with Ubuntu
wsl --install

# Or install specific Ubuntu version
wsl --install -d Ubuntu-24.04
```

### 1.2 Restart Your Computer

After installation, restart Windows.

### 1.3 Complete Ubuntu Setup

1. Open **Ubuntu** from Start Menu
2. Create username and password
3. Update packages:

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.4 Verify WSL2

```bash
wsl --list --verbose
```

Should show:
```
  NAME            STATE           VERSION
* Ubuntu-24.04    Running         2
```

---

## Step 2: Install Docker Desktop

### 2.1 Download & Install

1. Download from [docker.com](https://www.docker.com/products/docker-desktop/)
2. Run installer
3. **Important**: Enable "Use WSL 2 based engine" during setup

### 2.2 Configure Docker Desktop

1. Open Docker Desktop
2. Go to **Settings** (gear icon)
3. **General**: ✅ Use the WSL 2 based engine
4. **Resources > WSL Integration**: 
   - ✅ Enable integration with my default WSL distro
   - ✅ Ubuntu-24.04
5. Click **Apply & Restart**

### 2.3 Fix Docker DNS (Important!)

Create Docker DNS config:

```bash
sudo mkdir -p /etc/docker
sudo nano /etc/docker/daemon.json
```

Add:
```json
{
    "dns": ["8.8.8.8", "8.8.4.4"]
}
```

Save and exit (Ctrl+X, Y, Enter)

**Restart Docker Desktop** from Windows system tray.

### 2.4 Verify Docker in WSL

```bash
docker --version
docker-compose --version
docker run hello-world
```

---

## Step 3: Setup Project

### 3.1 Create Project Directory

```bash
# Create projects folder
mkdir -p ~/projects
cd ~/projects

# Clone your repository (or copy files)
git clone <your-repo-url> server-rag
cd server-rag
```

### 3.2 Open Project in VS Code

```bash
code .
```

---

## Step 4: Install UV (Python Package Manager)

### 4.1 Install UV

```bash
# Install UV (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
source $HOME/.local/bin/env

# Or add to .bashrc for persistence
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 4.2 Verify UV Installation

```bash
uv --version
```

### 4.3 Create Virtual Environment (Optional - for local dev without Docker)

```bash
cd ~/projects/server-rag

# Create venv with specific Python version
uv venv --python 3.11

# Activate
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

---

## Step 5: Install Supabase CLI

### 5.1 Install via npm (Recommended)

```bash
# Install Node.js if not present
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Supabase CLI locally (use with npx)
npm install supabase --save-dev
```

### 5.2 Or Install Globally

```bash
sudo npm install -g supabase
```

### 5.3 Verify Installation

```bash
# If installed locally (recommended)
npx supabase --version

# If installed globally
supabase --version
```

---

## Step 6: Configure Environment

### 6.1 Create .env File

```bash
cp .env.example .env
nano .env
```

### 6.2 Fill in Environment Variables

```properties
# =============================================================================
# Application Configuration
# =============================================================================
PROJECT_NAME="Six Figure RAG"
API_V1_PREFIX="/api"
DEBUG=false
DOMAIN=http://localhost:3000

# CORS - Add your frontend URL
ALLOWED_ORIGINS=http://localhost:3000

# =============================================================================
# Supabase Configuration (Local)
# =============================================================================
# These will be updated after running 'supabase start'
SUPABASE_API_URL=http://host.docker.internal:54321
SUPABASE_SERVICE_KEY=<your-service-role-key>

# =============================================================================
# Redis & Celery (Docker container names)
# =============================================================================
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# =============================================================================
# AWS S3 Configuration
# =============================================================================
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
AWS_REGION=ap-south-1
S3_BUCKET_NAME=<your-bucket-name>

# =============================================================================
# LLM & Embeddings (OpenRouter)
# =============================================================================
OPENROUTER_API_KEY=<your-openrouter-api-key>
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_LLM_MODEL=gpt-4-turbo
DEFAULT_EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSIONS=1536

# =============================================================================
# Clerk Authentication
# =============================================================================
CLERK_SECRET_KEY=<your-clerk-secret-key>
CLERK_WEBHOOK_SECRET=<your-clerk-webhook-secret>

# =============================================================================
# ScrapingBee (URL Processing)
# =============================================================================
SCRAPINGBEE_API_KEY=<your-scrapingbee-api-key>
```

---

## Step 7: Start Supabase

### 7.1 Initialize Supabase (First Time Only)

```bash
cd ~/projects/server-rag

# If supabase folder doesn't exist
npx supabase init
```

### 7.2 Start Supabase

```bash
npx supabase start
```

**Wait for it to complete** (downloads Docker images on first run).

### 7.3 Get Service Role Key

After `npx supabase start`, you'll see:

```
         API URL: http://127.0.0.1:54321
          DB URL: postgresql://postgres:postgres@127.0.0.1:54322/postgres
      Studio URL: http://127.0.0.1:54323
        anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  ← COPY THIS
```

### 7.4 Update .env with Service Key

```bash
nano .env
```

Update:
```properties
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 7.5 Run Migrations

```bash
# Apply all migrations
npx supabase db reset
```

This creates all tables, indexes, and RPC functions.

### 7.6 Verify in Supabase Studio

Open browser: http://127.0.0.1:54323

Check **Table Editor** - you should see:
- users
- projects
- project_settings
- project_documents
- document_chunks
- chats
- messages

---

## Step 8: Run the Application

### 8.1 Create .dockerignore

```bash
nano .dockerignore
```

Add:
```
.git
.gitignore
__pycache__
*.py[cod]
.venv
venv
.env.*
*.md
tests/
supabase/.branches
supabase/.temp
```

### 8.2 Build Docker Images

```bash
docker-compose build --no-cache
```

### 8.3 Start All Services

```bash
docker-compose up -d
```

### 8.4 Check Status

```bash
# See running containers
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f celery-worker
```

---

## Step 9: Verify Setup

### 9.1 Check API Health

```bash
curl http://localhost:8000/health
```

Should return:
```json
{"status": "healthy"}
```

### 9.2 Check API Docs

Open browser: http://localhost:8000/api/docs

### 9.3 Check Flower (Celery Monitor)

Open browser: http://localhost:5555

### 9.4 Check All Services

| Service | URL | Purpose |
|---------|-----|---------|
| FastAPI | http://localhost:8000 | Main API |
| API Docs | http://localhost:8000/api/docs | Swagger UI |
| Supabase Studio | http://localhost:54323 | Database UI |
| Flower | http://localhost:5555 | Celery Monitor |

---

## Project Structure

```
server-rag/
├── src/
│   ├── api/                    # API Layer
│   │   ├── deps.py             # Dependencies (auth)
│   │   └── v1/
│   │       ├── router.py       # Route aggregation
│   │       └── endpoints/
│   │           ├── projects.py
│   │           ├── files.py
│   │           ├── chats.py
│   │           ├── messages.py
│   │           └── webhooks.py
│   │
│   ├── core/                   # Core utilities
│   │   ├── security.py         # Clerk auth
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── middleware.py       # Logging middleware
│   │
│   ├── models/
│   │   └── enums.py            # All enumerations
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── common.py
│   │   ├── project.py
│   │   ├── file.py
│   │   ├── chat.py
│   │   └── user.py
│   │
│   ├── services/               # Business logic
│   │   ├── database/
│   │   │   ├── supabase.py
│   │   │   └── repositories/
│   │   ├── storage/
│   │   │   └── s3.py
│   │   ├── cache/
│   │   │   └── redis.py
│   │   ├── llm/
│   │   │   ├── embeddings.py
│   │   │   ├── chat.py
│   │   │   └── providers/
│   │   └── document/
│   │       ├── parser.py
│   │       ├── chunker.py
│   │       └── processor.py
│   │
│   ├── rag/                    # RAG Pipeline
│   │   ├── pipeline.py
│   │   ├── vector_search.py
│   │   ├── keyword_search.py
│   │   ├── hybrid_search.py
│   │   ├── rrf.py
│   │   ├── query_expansion.py
│   │   ├── context_builder.py
│   │   └── prompt_builder.py
│   │
│   ├── tasks/                  # Celery tasks
│   │   ├── celery_app.py
│   │   └── document_tasks.py
│   │
│   ├── config.py               # Settings
│   └── main.py                 # FastAPI app
│
├── supabase/
│   ├── migrations/
│   │   └── 20241214000000_initial_schema.sql
│   ├── config.toml
│   └── seed.sql
│
├── docker/
│   ├── Dockerfile
│   └── Dockerfile.celery
│
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── .env
├── .env.example
├── .dockerignore
└── README.md
```

---

## API Endpoints

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects` | List all projects |
| POST | `/api/projects` | Create project |
| GET | `/api/projects/{id}` | Get project |
| DELETE | `/api/projects/{id}` | Delete project |
| GET | `/api/projects/{id}/settings` | Get settings |
| PUT | `/api/projects/{id}/settings` | Update settings |
| GET | `/api/projects/{id}/chats` | Get project chats |

### Files
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects/{id}/files` | List files |
| POST | `/api/projects/{id}/files/upload-url` | Get upload URL |
| POST | `/api/projects/{id}/files/confirm` | Confirm upload |
| POST | `/api/projects/{id}/urls` | Add URL |
| DELETE | `/api/projects/{id}/files/{file_id}` | Delete file |
| GET | `/api/projects/{id}/files/{file_id}/chunks` | Get chunks |

### Chats
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chats` | Create chat |
| GET | `/api/chats/{id}` | Get chat with messages |
| DELETE | `/api/chats/{id}` | Delete chat |

### Messages
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects/{project_id}/chats/{chat_id}/messages` | Send message (RAG) |

### Webhooks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/webhook/clerk` | Clerk webhook |

---

## Common Issues & Fixes

### 1. Docker DNS Issues

**Error**: `failed to lookup address information`

**Fix**:
```bash
sudo nano /etc/docker/daemon.json
```
Add:
```json
{"dns": ["8.8.8.8", "8.8.4.4"]}
```
Restart Docker Desktop.

---

### 2. Redis Connection Failed

**Error**: `Redis connection failed - caching disabled`

**Fix**: Check `.env` uses container name:
```properties
REDIS_URL=redis://redis:6379/0
```
NOT `localhost`.

---

### 3. Supabase Connection Refused

**Error**: `httpx.ConnectError: Connection refused`

**Fix**: Use `host.docker.internal` in `.env`:
```properties
SUPABASE_API_URL=http://host.docker.internal:54321
```

---

## Useful Commands

### Docker

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f api
docker-compose logs -f celery-worker

# Rebuild specific service
docker-compose build --no-cache api
docker-compose up -d api

# Enter container shell
docker-compose exec api bash

# Remove all containers and images
docker-compose down --rmi all --volumes
```

### Supabase

```bash
# Start Supabase
npx supabase start

# Stop Supabase
npx supabase stop

# Reset database (run all migrations)
npx supabase db reset

# Check status
npx supabase status

# View logs
npx supabase logs
```

### Development

```bash
# Code changes in src/ → Auto-reload (no restart needed)

# .env changes
docker-compose up -d

# requirements.txt changes
docker-compose build --no-cache
docker-compose up -d
```

### UV (Python Package Manager)

```bash
# Create virtual environment
uv venv --python 3.11

# Activate venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Add new package
uv pip install package-name

# Sync with requirements.txt
uv pip sync requirements.txt
```

### Ngrok (Public URL for Webhooks)

```bash
# Install ngrok
snap install ngrok

# Expose API
ngrok http 8000

# Use the https URL for Clerk webhooks
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI |
| **Database** | Supabase (PostgreSQL + pgvector) |
| **Cache/Queue** | Redis |
| **Task Queue** | Celery |
| **Auth** | Clerk |
| **Storage** | AWS S3 |
| **LLM** | OpenRouter (GPT-4) |
| **Embeddings** | text-embedding-3-large |
| **Document Processing** | Unstructured |
| **Containerization** | Docker |

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js       │────▶│   FastAPI       │────▶│   Supabase      │
│   Frontend      │     │   Backend       │     │   (pgvector)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   Redis         │
                        │   (Cache/Queue) │
                        └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   Celery        │
                        │   Workers       │
                        └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   AWS S3        │
                        │   (Storage)     │
                        └─────────────────┘
```