# SAP OS & HANA Infrastructure Monitoring Platform with AI Analytics

## Overview

A centralized, AI-driven monitoring platform for SAP infrastructure (ECC, S/4HANA, BW) with real-time metrics, predictive analytics, and root cause analysis using locally hosted LLM models.

### Key Features

✅ **Agentless SSH-based Monitoring** - No agents to install  
✅ **Multi-System Support** - ECC, S/4HANA, BW, HANA databases  
✅ **AI-Powered Analytics** - Local LLM for RCA and predictions  
✅ **Real-Time Dashboards** - WebSocket-enabled React UI  
✅ **Backup Monitoring** - NAS mount and backup health tracking  
✅ **Predictive Alerts** - Failure forecasting and trend analysis  
✅ **Distributed Architecture** - Horizontal scalability with Docker  
✅ **Time-Series Database** - TimescaleDB for metrics retention  

---

## Architecture

```
┌─────────────────────────────────────┐
│      React Web Dashboard (Port 3000)│
└────────────────┬────────────────────┘
                 │ WebSocket
                 ▼
┌─────────────────────────────────────┐
│  FastAPI Backend (Port 8000)        │
│  - REST API                         │
│  - JWT Authentication               │
│  - Real-time Updates                │
└────────────────┬────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│ SSH    │  │ AI     │  │ Redis  │
│Collect │  │Engine  │  │Cache   │
│(Async) │  │(Ollama)│  │        │
└────────┘  └────────┘  └────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  PostgreSQL + TimescaleDB (Port 5432)│
│  - 30-day metric retention          │
│  - Time-series optimization         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  SAP Servers (ECC, S/4HANA, BW, HANA)│
└─────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React, Tailwind CSS, Recharts, WebSocket |
| **Backend** | FastAPI, AsyncIO, SQLAlchemy ORM |
| **Database** | PostgreSQL 15 + TimescaleDB |
| **AI Engine** | Ollama + Llama 3.1 / Qwen |
| **SSH Protocol** | AsyncSSH (parallel execution) |
| **Caching** | Redis |
| **Task Queue** | APScheduler |
| **Containerization** | Docker & Docker Compose |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- SSH access to target SAP servers

### Installation

```bash
# Clone repository
git clone https://github.com/shibinbalakrishna/sap-monitor.git
cd sap-monitor

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Access Services

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| Dashboard | http://localhost:3000 | (React app) |
| API Docs | http://localhost:8000/docs | (Swagger UI) |
| API | http://localhost:8000 | JWT required |
| Database | localhost:5432 | postgres/postgres |
| Ollama | http://localhost:11434 | (AI engine) |
| Redis | localhost:6379 | (Cache) |

---

## Project Structure

```
sap-monitor/
├── backend/                      # FastAPI application
│   ├── main.py                  # Application entry point
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile               # Backend container image
│   ├── config/
│   │   ├── settings.py          # Configuration management
│   │   └── database.py          # SQLAlchemy async setup
│   ├── models/
│   │   └── database.py          # ORM models for all entities
│   ├── routes/                  # API endpoint stubs
│   │   ├── servers.py           # Server CRUD operations
│   │   ├── metrics.py           # Metrics retrieval
│   │   ├── alerts.py            # Alert management
│   │   └── ai.py                # AI analytics endpoints
│   ├── services/                # Business logic layer
│   ├── middleware/              # Custom middleware
│   └── utils/                   # Helper functions
│
├── frontend/                     # React application
│   ├── Dockerfile               # Frontend container image
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
│   └── public/
│
├── collectors/                   # SSH monitoring agents
│   ├── ssh_client.py            # AsyncSSH wrapper
│   ├── os_metrics.py            # Linux OS metrics
│   ├── sap_monitor.py           # SAP process monitoring
│   ├── hana_monitor.py          # HANA database monitoring
│   ├── backup_monitor.py        # NAS backup monitoring
│   └── scheduler.py             # APScheduler configuration
│
├── ai/                           # AI analytics engine
│   ├── llm_engine.py            # Ollama integration
│   ├── anomaly_detection.py     # Anomaly scoring
│   ├── rca_engine.py            # Root cause analysis
│   ├── predictor.py             # Failure prediction
│   └── summarizer.py            # AI summaries
│
├── database/                     # Database initialization
│   └── init.sql                 # Schema creation script
│
├── docker/                       # Docker configurations
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── Dockerfile.collector
│
├── docker-compose.yml            # Multi-container orchestration
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

---

## Database Schema

### Core Tables

**servers** - System inventory
```sql
CREATE TABLE servers (
  id UUID PRIMARY KEY,
  sid VARCHAR(3) NOT NULL,
  hostname VARCHAR(255) NOT NULL,
  system_type VARCHAR(50),        -- ECC, S/4HANA, BW
  db_type VARCHAR(50),             -- HANA, ASE, Oracle
  backup_path VARCHAR(500),
  ssh_host VARCHAR(255),
  ssh_user VARCHAR(100),
  ssh_password_encrypted VARCHAR(500),
  ssh_port INT DEFAULT 22,
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**metrics** - Time-series performance data (30-day retention)
```sql
CREATE TABLE metrics (
  time TIMESTAMP NOT NULL,
  server_id UUID NOT NULL REFERENCES servers(id),
  cpu_usage FLOAT,
  cpu_load FLOAT,
  memory_usage FLOAT,
  memory_available FLOAT,
  swap_used FLOAT,
  network_in FLOAT,
  network_out FLOAT,
  disk_io_read FLOAT,
  disk_io_write FLOAT
);
SELECT create_hypertable('metrics', 'time', if_not_exists => TRUE);
```

**filesystems** - Disk space monitoring
```sql
CREATE TABLE filesystems (
  id UUID PRIMARY KEY,
  server_id UUID NOT NULL REFERENCES servers(id),
  mount_point VARCHAR(500),
  total_size BIGINT,
  used_size BIGINT,
  available_size BIGINT,
  inode_total BIGINT,
  inode_used BIGINT,
  last_checked TIMESTAMP DEFAULT NOW()
);
```

**sap_processes** - SAP instance monitoring
```sql
CREATE TABLE sap_processes (
  id UUID PRIMARY KEY,
  server_id UUID NOT NULL REFERENCES servers(id),
  process_name VARCHAR(100),      -- dispatcher, gateway, enqueue, msg_server
  status VARCHAR(50),              -- running, stopped, crashed
  pid INT,
  memory_mb FLOAT,
  cpu_percent FLOAT,
  last_checked TIMESTAMP DEFAULT NOW()
);
```

**hana_backups** - HANA backup catalog
```sql
CREATE TABLE hana_backups (
  id UUID PRIMARY KEY,
  server_id UUID NOT NULL REFERENCES servers(id),
  backup_id VARCHAR(100),
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  status VARCHAR(50),              -- SUCCESS, FAILED, IN_PROGRESS
  backup_size_gb FLOAT,
  data_backed_up_gb FLOAT,
  catalog_size_gb FLOAT
);
```

**nas_mounts** - NAS backup mount monitoring
```sql
CREATE TABLE nas_mounts (
  id UUID PRIMARY KEY,
  server_id UUID NOT NULL REFERENCES servers(id),
  mount_path VARCHAR(500),        -- /hana/backup
  nfs_server VARCHAR(255),
  status VARCHAR(50),              -- mounted, unmounted, timeout
  latency_ms FLOAT,
  last_response_time TIMESTAMP DEFAULT NOW()
);
```

**alerts** - Alert management
```sql
CREATE TABLE alerts (
  id UUID PRIMARY KEY,
  server_id UUID REFERENCES servers(id),
  severity VARCHAR(50),            -- INFO, WARNING, CRITICAL
  alert_type VARCHAR(100),         -- CPU_HIGH, DISK_FULL, BACKUP_FAILED
  message TEXT,
  status VARCHAR(50),              -- NEW, ACKNOWLEDGED, RESOLVED
  created_at TIMESTAMP DEFAULT NOW(),
  resolved_at TIMESTAMP,
  INDEX idx_severity (severity)
);
```

**ai_analysis** - AI-generated insights
```sql
CREATE TABLE ai_analysis (
  id UUID PRIMARY KEY,
  server_id UUID NOT NULL REFERENCES servers(id),
  analysis_type VARCHAR(100),     -- RCA, PREDICTION, SUMMARY
  summary TEXT,
  confidence_score FLOAT,
  correlated_metrics JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**users** - RBAC support
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(500),
  role VARCHAR(50),               -- admin, basis_team, infra_team, viewer
  enabled BOOLEAN DEFAULT true,
  last_login TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**audit_logs** - Compliance tracking
```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  action VARCHAR(100),
  resource_type VARCHAR(100),
  resource_id UUID,
  changes JSONB,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## API Endpoints

### Servers
```
GET    /api/servers              # List all servers
POST   /api/servers              # Add new server
GET    /api/servers/{server_id}  # Get server details
PUT    /api/servers/{server_id}  # Edit server
DELETE /api/servers/{server_id}  # Remove server
```

### Metrics
```
GET    /api/metrics              # Get latest metrics
GET    /api/metrics/{server_id}  # Get server metrics
GET    /api/metrics/history      # Get historical metrics
```

### Alerts
```
GET    /api/alerts               # List alerts
POST   /api/alerts/{alert_id}/acknowledge  # Acknowledge alert
DELETE /api/alerts/{alert_id}    # Resolve alert
```

### AI Analytics
```
GET    /api/ai/summary/{server_id}       # Get AI incident summary
GET    /api/ai/prediction/{server_id}    # Get failure predictions
GET    /api/ai/rca/{alert_id}            # Root cause analysis
```

---

## Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/sap_monitor
DATABASE_ECHO=false

# Backend API
FAST_API_HOST=0.0.0.0
FAST_API_PORT=8000
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Frontend
REACT_APP_API_URL=http://localhost:8000

# SSH Monitoring
SSH_TIMEOUT=10
SSH_RETRIES=3
SSH_PARALLEL_WORKERS=10

# AI/LLM
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama2
OLLAMA_TEMPERATURE=0.7

# Redis
REDIS_URL=redis://redis:6379/0

# Logging
LOG_LEVEL=INFO
```

---

## Monitoring Features

### OS Metrics (Linux)
- CPU utilization, load average, context switches
- Memory usage, swap, cache
- Disk I/O, filesystem usage, inode tracking
- Network traffic, connections
- Process list, top processes

### SAP Monitoring
- Instance status (dispatcher, gateway, enqueue, message server)
- Process health and resource usage
- Dialog response times
- Batch job status
- Gateway connectivity

### HANA Database
- Backup catalog status
- Memory utilization (row/column store)
- Expensive SQL statements
- Active transactions
- Replication lag (if applicable)

### NAS Backup
- Mount availability
- Backup success/failure
- Backup duration and throughput
- Storage capacity and growth trends
- NFS latency monitoring

---

## AI Analytics

### Capabilities

**1. Real-Time Incident Summaries**
```
Input:  CPU spike 85%, Memory 92%, Backup running
Output: "Backup job consuming 18GB RAM, elevated CPU expected. ETA: 45 min"
```

**2. Predictive Analytics**
```
Input:  Disk utilization trending +2GB/day
Output: "Disk full in 30 days unless action taken"
```

**3. Root Cause Analysis**
```
Input:  Gateway crash, NAS latency spike, backup timeout
Output: "NAS timeout caused backup failure, triggering gateway disconnect"
```

**4. Trend Analysis**
```
Input:  Historical metrics over 30 days
Output: "Monday backup 8% slower than week average"
```

### LLM Configuration

Supported models via Ollama:
- **Llama 3.1 8B** - General RCA and summaries
- **Qwen 14B** - Better reasoning and correlation
- **Mistral Small** - Lightweight deployments

---

## Deployment

### Docker Compose (Development)

```bash
docker-compose up -d
```

Services:
- Backend (FastAPI)
- Frontend (React)
- Database (PostgreSQL + TimescaleDB)
- Cache (Redis)
- AI Engine (Ollama)
- Health checks on all services

### Kubernetes (Future)

Ready for:
- Helm charts
- StatefulSets for database
- Deployments for services
- ConfigMaps for configuration
- Persistent volumes for data

---

## Security

- ✅ JWT token-based authentication
- ✅ SSH password encryption (Fernet)
- ✅ RBAC with role-based access
- ✅ Audit logging for all changes
- ✅ CORS configuration
- ✅ SQL injection prevention (ORM)
- ✅ Rate limiting ready

---

## Performance

| Metric | Target |
|--------|--------|
| Dashboard response | < 3 seconds |
| API endpoint response | < 500ms |
| Metric ingestion | < 1 minute |
| SSH execution timeout | 10 seconds |
| Max monitored servers | 100+ |
| Concurrent SSH connections | 50+ |

---

## Roadmap

**Phase 1 (Current)**
- ✅ Project structure
- ✅ Database schema
- ⏳ SSH collectors
- ⏳ Backend API implementation
- ⏳ Frontend dashboard

**Phase 2**
- SSH key authentication
- Advanced AI analytics
- Kubernetes deployment
- Multi-tenant architecture

**Phase 3**
- Auto-remediation
- SAPControl automation
- SAP Solution Manager integration
- Predictive capacity planning

---

## Contributing

Contributions welcome! Please:
1. Create feature branch from `main`
2. Commit with clear messages
3. Push and create Pull Request
4. Ensure all tests pass

---

## License

MIT License - See LICENSE file

---

## Support

- 📧 Email: shibinbalakrishna@example.com
- 📖 Docs: See `/docs` folder
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

**Built with ❤️ for SAP Infrastructure Monitoring**
