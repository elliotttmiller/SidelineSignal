# SidelineSignal - Autonomous Streaming Site Monitoring System

**Professional Operational Playbook for Autonomous Deployment**

SidelineSignal is a production-ready, autonomous monitoring system designed to discover, verify, and continuously monitor streaming sites with minimal human intervention. This system operates as a self-sustaining ecosystem where intelligent discovery feeds real-time monitoring through a shared data infrastructure.

## Project Overview

SidelineSignal implements a dual-component architecture that enables fully autonomous operation:

- **Signal Scout**: An intelligent discovery engine that autonomously finds and verifies streaming sites
- **Sideline App**: A real-time monitoring web application that provides status insights and API access
- **Shared Data Store**: A central SQLite database that enables loose coupling and data persistence

The system is designed for unattended operation, capable of running indefinitely with periodic scout executions that maintain an up-to-date database of verified streaming sites.

## Architecture

### Autonomous Ecosystem Design

The SidelineSignal architecture follows a producer-consumer pattern with autonomous feedback loops:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Signal Scout   │───▶│  Shared Database │◀───│  Sideline App   │
│   (Discovery)   │    │   (sites.db)     │    │  (Monitoring)   │
│                 │    │                  │    │                 │
│ • URL Discovery │    │ • Site Registry  │    │ • Status Checks │
│ • Verification  │    │ • Confidence     │    │ • Web Interface │
│ • Self-Healing  │    │ • Metadata       │    │ • API Endpoint  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        ▲                         │                        │
        │                         ▼                        │
        └─────────── Autonomous Loop ◀─────────────────────┘
```

### Key Architectural Principles

1. **Autonomous Operation**: The Scout operates independently, requiring no manual intervention
2. **Self-Healing**: Failed sites are automatically deactivated after repeated verification failures  
3. **Configuration-Driven**: All operational parameters externalized for dynamic control
4. **Loose Coupling**: Components communicate only through the shared database
5. **Scalable Design**: Components can be deployed and scaled independently

### Component Details

#### Signal Scout (`signal_scout/`)
**Purpose**: Autonomous site discovery and verification engine

**Core Modules**:
- `scout.py` - Main orchestration engine with configuration management
- `hunters.py` - Multi-strategy URL discovery (Community Aggregator + Permutation Verifier)
- `verification.py` - Multi-stage verification pipeline with confidence scoring
- `scout_config.json` - Externalized operational parameters

**Key Capabilities**:
- Configurable discovery strategies with externalized parameters
- Advanced verification with confidence scoring and failure tolerance
- Automatic database maintenance and site lifecycle management
- Comprehensive logging and reporting

#### Sideline App (`sideline_app/`)
**Purpose**: Real-time monitoring interface with concurrent status checking

**Core Features**:
- Dynamic site loading from shared database
- Concurrent status verification for optimal performance
- RESTful API endpoint (`/api/statuses`) with enriched data
- Status change tracking and logging
- Responsive web interface for operational oversight

#### Shared Database (`shared_data/sites.db`)
**Purpose**: Central data store enabling component coordination

**Schema**:
```sql
CREATE TABLE sites (
    id INTEGER PRIMARY KEY,
    name TEXT,
    url TEXT UNIQUE,
    source TEXT,                    -- Discovery source identifier
    last_verified DATETIME,         -- Timestamp of last verification
    confidence_score INTEGER,       -- Verification confidence (0-100)
    is_active BOOLEAN              -- Active status for monitoring
);
```

## Setup and Installation

### Prerequisites

SidelineSignal requires Python 3.8+ and uses separate virtual environments for operational isolation.

### Dual Virtual Environment Setup

**Scout Environment Setup**:
```bash
# Create and activate scout virtual environment
python -m venv scout_venv
source scout_venv/bin/activate    # Linux/Mac
# scout_venv\Scripts\activate     # Windows

# Install scout dependencies
pip install -r requirements_scout.txt
deactivate
```

**App Environment Setup**:
```bash
# Create and activate app virtual environment
python -m venv app_venv
source app_venv/bin/activate      # Linux/Mac  
# app_venv\Scripts\activate       # Windows

# Install app dependencies
pip install -r requirements_app.txt
deactivate
```

### Configuration Management

The Scout's behavior is controlled entirely through `signal_scout/scout_config.json`:

```json
{
  "operational_parameters": {
    "aggregator_urls": [
      "https://github.com/fmhy/FMHYedit/wiki/📺-Movies---TV"
    ],
    "permutation_bases": [
      "streameast", "sportssurge", "freestreams", "watchseries", "moviehd"
    ],
    "permutation_tlds": [
      ".app", ".io", ".live", ".gg", ".net", ".org", ".tv", ".me", ".co", ".cc"
    ]
  },
  "discovery_settings": {
    "max_concurrent_verifications": 10,
    "request_timeout": 5,
    "verification_confidence_threshold": 50
  },
  "maintenance_settings": {
    "deactivation_hours": 24,
    "max_failed_attempts": 3,
    "cleanup_stale_sites": true
  }
}
```

**Configuration Parameters**:
- `aggregator_urls`: URLs to scrape for community-curated sites
- `permutation_bases`: Base domain names for permutation discovery
- `permutation_tlds`: Top-level domains to test with base names
- `verification_confidence_threshold`: Minimum confidence score for site activation
- `deactivation_hours`: Hours before failing sites are deactivated

## Usage

### Development and Testing

**Manual Scout Execution**:
```bash
source scout_venv/bin/activate
cd signal_scout/
python scout.py
deactivate
```

**Web Application Launch**:
```bash
source app_venv/bin/activate
cd sideline_app/
python app.py
# Access at http://localhost:5000
deactivate
```

**API Access**:
```bash
# Get current status of all monitored sites
curl http://localhost:5000/api/statuses | jq .
```

### System Validation

Use the comprehensive testing procedure in `TESTING_PROCEDURE.md` to certify autonomous operation:

1. **Environment Preparation**: Set up dual virtual environments
2. **Baseline Scout Execution**: Establish initial database state
3. **Application Integration Test**: Verify web interface and API functionality
4. **Autonomous Loop Validation**: Execute Scout→App→Scout cycle validation
5. **Extended Soak Test**: Long-term stability testing

### Database Operations

**Database Inspection**:
```bash
# Check total sites in database
sqlite3 shared_data/sites.db "SELECT COUNT(*) FROM sites;"

# View active sites with details
sqlite3 shared_data/sites.db "SELECT name, url, source, confidence_score, last_verified FROM sites WHERE is_active = 1;"

# Check discovery sources
sqlite3 shared_data/sites.db "SELECT source, COUNT(*) as count FROM sites GROUP BY source;"
```

**Database Maintenance**:
```bash
# Reset database (will be recreated on next Scout run)
rm shared_data/sites.db

# Backup database
cp shared_data/sites.db shared_data/sites.db.backup
```

### Monitoring and Logging

**Log Files**:
- `signal_scout/scout.log` - Scout discovery and verification events
- `sideline_app/status_changes.log` - Site status change history

**Key Metrics to Monitor**:
- Discovery success rate (URLs found vs verified)
- Verification confidence scores  
- Site activation/deactivation patterns
- Response times and error rates

## Production Deployment & Autonomy

### Production Stack Requirements

For unattended production operation, SidelineSignal requires:

**Web Server**: Gunicorn WSGI server for the Sideline App
```bash
# Install Gunicorn in app environment
source app_venv/bin/activate
pip install gunicorn
```

**Reverse Proxy**: Nginx for production web serving
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

**Process Management**: systemd service files for reliable process management

### Production Deployment Steps

1. **Deploy Application Code**:
   ```bash
   # Clone repository to production server
   git clone https://github.com/elliotttmiller/SidelineSignal.git /opt/sidelinesignal
   cd /opt/sidelinesignal
   ```

2. **Set Up Production Virtual Environments**:
   ```bash
   # Scout environment
   python -m venv /opt/sidelinesignal/scout_venv
   source /opt/sidelinesignal/scout_venv/bin/activate
   pip install -r requirements_scout.txt
   deactivate

   # App environment with Gunicorn
   python -m venv /opt/sidelinesignal/app_venv  
   source /opt/sidelinesignal/app_venv/bin/activate
   pip install -r requirements_app.txt
   pip install gunicorn
   deactivate
   ```

3. **Configure Gunicorn Service**:
   ```bash
   # Create Gunicorn configuration
   cat > /opt/sidelinesignal/gunicorn.conf.py << EOF
   bind = "127.0.0.1:5000"
   workers = 2
   timeout = 30
   keepalive = 2
   max_requests = 1000
   max_requests_jitter = 50
   EOF
   ```

4. **Create systemd Service File**:
   ```bash
   sudo cat > /etc/systemd/system/sidelinesignal.service << EOF
   [Unit]
   Description=SidelineSignal Monitoring Application
   After=network.target

   [Service]
   User=sidelinesignal
   Group=sidelinesignal
   WorkingDirectory=/opt/sidelinesignal/sideline_app
   Environment=PATH=/opt/sidelinesignal/app_venv/bin
   ExecStart=/opt/sidelinesignal/app_venv/bin/gunicorn -c ../gunicorn.conf.py app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   EOF

   sudo systemctl daemon-reload
   sudo systemctl enable sidelinesignal
   sudo systemctl start sidelinesignal
   ```

5. **Configure Nginx Reverse Proxy**:
   ```bash
   sudo cat > /etc/nginx/sites-available/sidelinesignal << EOF
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
       }
   }
   EOF

   sudo ln -s /etc/nginx/sites-available/sidelinesignal /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```

### Enabling Autonomous Operation

The key to autonomous operation is scheduling the Signal Scout to run automatically. This is achieved through a cron job that executes the scout periodically:

**Production Cron Job Configuration**:
```bash
# Open crontab for editing
crontab -e

# Add the following line for autonomous operation (runs every 6 hours)
0 */6 * * * /opt/sidelinesignal/scout_venv/bin/python /opt/sidelinesignal/signal_scout/scout.py >> /var/log/sidelinesignal-scout.log 2>&1

# Alternative schedules:
# Every 4 hours: 0 */4 * * *
# Every 12 hours: 0 */12 * * *  
# Daily at 2 AM: 0 2 * * *
# Twice daily: 0 2,14 * * *
```

**Cron Job Explanation**:
- `0 */6 * * *` - Execute at minute 0 of every 6th hour
- `/opt/sidelinesignal/scout_venv/bin/python` - Use Scout virtual environment Python
- `/opt/sidelinesignal/signal_scout/scout.py` - Execute Scout discovery script
- `>> /var/log/sidelinesignal-scout.log 2>&1` - Log output and errors

**Verify Autonomous Operation**:
```bash
# Check cron job status
crontab -l

# Monitor cron execution logs
tail -f /var/log/sidelinesignal-scout.log

# Verify database updates
sqlite3 /opt/sidelinesignal/shared_data/sites.db "SELECT MAX(last_verified) FROM sites;"
```

### Production Monitoring

**Health Checks**:
```bash
# Application health
curl -f http://localhost/api/statuses > /dev/null || echo "App down"

# Database health  
sqlite3 /opt/sidelinesignal/shared_data/sites.db "SELECT COUNT(*) FROM sites WHERE is_active = 1;" || echo "DB error"

# Scout logs health
tail -n 10 /var/log/sidelinesignal-scout.log | grep -q "DISCOVERY CYCLE COMPLETE" || echo "Scout error"
```

**Log Rotation**:
```bash
sudo cat > /etc/logrotate.d/sidelinesignal << EOF
/var/log/sidelinesignal-scout.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    create 644 sidelinesignal sidelinesignal
}
EOF
```

### Autonomous System Characteristics

Once deployed with the cron job, SidelineSignal operates as a truly autonomous system:

- **Self-Discovery**: Continuously finds new streaming sites using multiple strategies
- **Self-Verification**: Validates site functionality and assigns confidence scores
- **Self-Healing**: Automatically deactivates failing sites to maintain data quality
- **Self-Reporting**: Provides real-time status through web interface and API
- **Self-Maintaining**: Manages database lifecycle and cleanup operations

The system requires no human intervention for normal operation, making it ideal for production environments where reliable, unattended monitoring is essential.

## Core Protocols

SidelineSignal operates according to five core protocols that ensure reliable autonomous operation:

1. **Unquestionable Reliability**: Robust error handling, graceful degradation, and automatic recovery
2. **User-Centric Performance**: Background processing with responsive interface and concurrent operations
3. **Absolute Clarity**: Clean data presentation, comprehensive logging, and operational transparency
4. **Scalable & Modular Design**: Independent components, externalized configuration, and flexible deployment
5. **Holistic Craftsmanship**: Professional quality, complete documentation, and production readiness

These protocols guide every aspect of the system's design and operation, ensuring it meets the highest standards for autonomous monitoring systems.