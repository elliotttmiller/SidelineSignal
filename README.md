# SidelineSignal V3 - Cognitive Autonomous Streaming Discovery System

**Professional V3 Operational Manual - AI-Powered Scrapy Architecture**

SidelineSignal V3 represents the evolution of autonomous streaming site discovery, featuring a sophisticated AI-powered cognitive crawler built on Scrapy architecture. This system combines machine learning classification with intelligent link analysis to autonomously discover, classify, and verify streaming sites with minimal human intervention.

## Project Overview

SidelineSignal V3 implements a cutting-edge cognitive architecture that elevates streaming site discovery to autonomous intelligence:

### Core Components

- **Signal Scout V3**: Scrapy-based cognitive crawler with AI classification engine
- **AI Classifier ("The Judge")**: Machine learning-powered content analysis and site classification  
- **V2 Verification Pipeline**: Multi-stage verification with confidence scoring and failure tolerance
- **Sideline App**: Real-time monitoring web application with concurrent status checking
- **Shared Database**: SQLite-based data persistence with autonomous lifecycle management

### Revolutionary V3 Features

**🧠 AI-Powered Content Classification**
- Real-time machine learning analysis of page content
- Sports and streaming keyword density analysis
- Technical streaming element detection (video tags, iframes, JavaScript players)
- Confidence-based decision making with transparent reasoning

**🕷️ Scrapy-Based Autonomous Crawler**
- Professional-grade web crawling with Scrapy framework
- Focused crawling with intelligent link relevancy scoring
- Autonomous feedback loops for continuous discovery
- Genesis seed engine for intelligent starting points

**⚡ Integrated Verification Pipeline**
- Seamless V3→V2 verification handoff
- Headless browser verification for dynamic content
- Multi-criteria confidence scoring and quarantine management
- Database lifecycle management with failure tracking

## Architecture

### V3 Cognitive Architecture Overview

SidelineSignal V3 implements a sophisticated cognitive architecture that transforms streaming site discovery from simple crawling to intelligent analysis:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SidelineSignal V3 Cognitive Engine                │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │
│  │  Genesis Seed   │    │  AI Classifier  │    │ V2 Verification │   │
│  │     Engine      │───▶│   "The Judge"   │───▶│    Pipeline     │   │
│  │                 │    │                 │    │                 │   │
│  │ • Query Engine  │    │ • ML Analysis   │    │ • Multi-Stage   │   │
│  │ • URL Discovery │    │ • Content DNA   │    │ • Confidence    │   │
│  │ • Seed Ranking  │    │ • Tech Detection│    │ • Quarantine    │   │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘   │
│           │                        │                        │        │
│           ▼                        ▼                        ▼        │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │              Scrapy Cognitive Crawler Framework                 │ │
│  │                                                                 │ │
│  │ • Focused Link Analysis     • Autonomous Feedback Loops        │ │
│  │ • Relevancy Scoring         • Professional Logging             │ │
│  │ • Depth-Limited Crawling    • Error Recovery & Retry           │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Shared Database Infrastructure                  │
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Site Registry │    │  Lifecycle Mgmt │    │ Monitoring Data │ │
│  │                 │    │                 │    │                 │ │
│  │ • Verified URLs │    │ • Quarantine    │    │ • Status Checks │ │
│  │ • Confidence    │    │ • Failure Count │    │ • API Endpoints │ │
│  │ • Source Track  │    │ • Auto-Cleanup  │    │ • Real-time UI  │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Sideline Monitoring App                      │
│                                                                     │
│     Web Interface + RESTful API + Concurrent Status Verification    │
└─────────────────────────────────────────────────────────────────────┘
```

### Cognitive Decision Flow

1. **Genesis Phase**: Query-based seed discovery and initial URL ranking
2. **Crawl Phase**: Focused Scrapy crawling with intelligent link evaluation  
3. **Classification Phase**: AI-powered content analysis and streaming site identification
4. **Verification Phase**: Multi-stage V2 verification with confidence scoring
5. **Integration Phase**: Database storage and monitoring system integration
6. **Feedback Phase**: Autonomous learning and seed queue enhancement

### Key Architectural Principles

1. **Cognitive Intelligence**: AI-driven decision making at every phase
2. **Autonomous Operation**: Self-sustaining discovery and verification cycles
3. **Professional Logging**: Complete operational transparency with detailed reasoning
4. **Modular Integration**: Seamless V3→V2 pipeline integration 
5. **Scalable Framework**: Scrapy-based architecture for enterprise deployment

## Setup and Installation

### Prerequisites

SidelineSignal V3 requires Python 3.8+ and uses dual virtual environments for operational isolation and component independence.

### Dual Virtual Environment Setup

The V3 architecture maintains separate environments for the Scrapy-based discovery engine and the monitoring application to ensure clean dependency management and deployment flexibility.

**Scout Environment Setup (V3 Cognitive Engine)**:
```bash
# Create and activate scout virtual environment  
python -m venv scout_venv
source scout_venv/bin/activate    # Linux/Mac
# scout_venv\Scripts\activate     # Windows

# Install V3 scout dependencies (includes Scrapy, ML libraries)
pip install -r requirements_scout.txt
deactivate
```

**App Environment Setup (Monitoring Interface)**:
```bash
# Create and activate app virtual environment
python -m venv app_venv
source app_venv/bin/activate      # Linux/Mac  
# app_venv\Scripts\activate       # Windows

# Install app dependencies (Flask, monitoring tools)
pip install -r requirements_app.txt
deactivate
```

### V3 Configuration Management

The V3 Scout's cognitive behavior is controlled through `signal_scout/scout_config.json` with enhanced AI and crawling parameters:

```json
{
  "operational_parameters": {
    "seed_queries": [
      "watch NFL live free",
      "soccer stream reddit", 
      "NBA live stream free",
      "MLB streaming sites"
    ],
    "aggregator_urls": [
      "https://github.com/fmhy/FMHYedit/wiki/📺-Movies---TV"
    ],
    "permutation_bases": [
      "streameast", "sportssurge", "freestreams", "watchseries"
    ],
    "permutation_tlds": [
      ".app", ".io", ".live", ".gg", ".net", ".org", ".tv"
    ]
  },
  "v3_crawler_settings": {
    "ai_confidence_threshold": 0.7,
    "max_crawl_depth": 3,
    "relevancy_threshold": 0.6,
    "enable_autonomous_feedback": true
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

**Key V3 Configuration Parameters**:
- `seed_queries`: Search terms for genesis seed URL discovery
- `ai_confidence_threshold`: Minimum AI classification score for V2 verification (0.0-1.0)
- `max_crawl_depth`: Maximum depth for focused crawling (prevents infinite loops)
- `relevancy_threshold`: Minimum link relevancy score for crawl inclusion (0.0-1.0)
- `enable_autonomous_feedback`: Enable verified sites to become new crawl seeds

## Training the AI Classifier

### Overview

The SidelineSignal V3 AI Classifier ("The Judge") is a machine learning component that analyzes web page content to identify streaming sites. The classifier uses a combination of content analysis, technical feature detection, and URL pattern recognition to make intelligent decisions about site classification.

### Training Data Structure

The AI classifier is trained on two sample files that define positive and negative examples:

**`signal_scout/positive_samples.txt`** - Contains URLs and text snippets from confirmed streaming sites:
```
# Example positive samples (streaming sites)
https://streameast.net - Live sports streaming with HD quality
https://sportsurge.net - Free NFL NBA MLB streams 
https://buffstreams.tv - Watch live sports online free
```

**`signal_scout/negative_samples.txt`** - Contains URLs and text snippets from non-streaming sites:
```
# Example negative samples (non-streaming sites)
https://espn.com/news - Sports news and information
https://wikipedia.org/sports - Sports encyclopedia articles
https://amazon.com/sports - Sports equipment shopping
```

### Training Process

To train or retrain the AI classifier with updated samples:

```bash
# Activate the scout virtual environment
source scout_venv/bin/activate

# Navigate to the scout directory
cd signal_scout/

# Execute the training script
python train_model.py

# Verify training completed successfully
ls -la scout_model.pkl
```

**Training Script Features**:
- **Feature Extraction**: Analyzes HTML content, URL patterns, and technical indicators
- **Model Training**: Uses scikit-learn with logistic regression and TF-IDF vectorization
- **Validation**: Performs cross-validation to ensure model accuracy
- **Persistence**: Saves trained model to `scout_model.pkl` for production use

### Model Features

The AI classifier analyzes multiple dimensions of web content:

**Technical DNA**:
- Video tags, iframes, and embed elements
- Streaming JavaScript libraries (JWPlayer, Video.js, HLS)
- DOM structure and link density

**Content DNA**:
- Sports keyword density analysis
- Streaming terminology detection
- Content-to-HTML ratio assessment

**URL DNA**:
- Domain pattern analysis
- Path structure evaluation
- Sports/streaming keyword presence

### Customizing the Classifier

To improve classification accuracy for specific types of streaming sites:

1. **Update Training Samples**: Add new positive/negative examples to the sample files
2. **Retrain Model**: Run `python train_model.py` to incorporate new data
3. **Test Performance**: Monitor AI classification results in operational logs
4. **Adjust Thresholds**: Modify `ai_confidence_threshold` in configuration for optimal performance

### Performance Monitoring

Monitor AI classifier performance through operational logs:
```bash
# View AI classification decisions in real-time
tail -f scout.log | grep "AI Classification"

# Analyze classification accuracy
grep "Classification result" scout.log | head -20
```

## Running the System

### V3 Scrapy-Based Discovery

The SidelineSignal V3 system is centered around the Scrapy-based cognitive crawler, which provides autonomous discovery with AI-powered intelligence.

**Execute V3 Cognitive Crawler**:
```bash
# Activate the scout virtual environment
source scout_venv/bin/activate

# Navigate to the scout directory  
cd signal_scout/

# Run the V3 cognitive crawler (production command)
scrapy crawl scout

# Alternative: Run with specific timeout (seconds)
# The spider is configured for 300 seconds (5 minutes) by default
scrapy crawl scout -s CLOSESPIDER_TIMEOUT=600

# Run with page limit for testing
scrapy crawl scout -s CLOSESPIDER_PAGECOUNT=50

deactivate
```

**V3 Crawler Features**:
- **Genesis Seed Engine**: Automatically discovers initial crawl targets from search queries
- **AI Classification**: Real-time machine learning analysis of every page
- **Focused Crawling**: Intelligent link selection with relevancy scoring
- **V2 Integration**: Seamless handoff to V2 verification pipeline
- **Professional Logging**: Complete operational transparency with detailed decision logs

**Legacy V2 Scout Execution** (for comparison/fallback):
```bash
source scout_venv/bin/activate
cd signal_scout/
python scout.py [v2|v3|hybrid]
deactivate
```

### Monitoring Web Application

**Launch Sideline Monitoring App**:
```bash
# Activate the app virtual environment
source app_venv/bin/activate

# Navigate to the app directory
cd sideline_app/

# Start the monitoring web application
python app.py

# Access the web interface
# URL: http://localhost:5000
# API: http://localhost:5000/api/statuses

deactivate
```

**Monitoring Features**:
- Real-time site status dashboard
- Concurrent site verification
- RESTful API for programmatic access
- Status change history and logging

### API Access

**RESTful API Endpoints**:
```bash
# Get current status of all monitored sites (JSON)
curl http://localhost:5000/api/statuses | jq .

# Get specific site information  
curl http://localhost:5000/api/sites | jq '.[] | select(.name=="Streameast")'

# Health check endpoint
curl http://localhost:5000/health
```

### Operational Workflows

**Daily Discovery Cycle**:
```bash
# 1. Run V3 cognitive discovery
source scout_venv/bin/activate && cd signal_scout/
scrapy crawl scout
deactivate

# 2. Launch monitoring for discovered sites
source app_venv/bin/activate && cd sideline_app/
python app.py
```

**Development Testing**:
```bash
# Short discovery run for testing
source scout_venv/bin/activate && cd signal_scout/
scrapy crawl scout -s CLOSESPIDER_PAGECOUNT=10 -s CLOSESPIDER_TIMEOUT=60
deactivate
```

**Performance Analysis**:
```bash
# Analyze recent crawl performance
tail -100 signal_scout/scout.log | grep "FINAL OPERATIONAL METRICS" -A 10

# View AI classification decisions
grep "Classification result" signal_scout/scout.log | tail -20

# Check database status after crawl
sqlite3 shared_data/sites.db "SELECT COUNT(*) as total, source FROM sites GROUP BY source;"
```

## Debugging and Operations

### Professional Logging System

SidelineSignal V3 implements comprehensive professional-grade logging that provides complete operational transparency and debugging capability.

**Primary Log File: `signal_scout/scout.log`**

The scout.log file contains detailed operational logs with professional formatting:
```
[2025-09-10 08:34:02] [INFO] SCOUT RUN STARTING - GENESIS SEED ENGINE ACTIVATED
[2025-09-10 08:34:02] [INFO] Initial seed queries being used: ['watch NFL live free', 'soccer stream reddit']
[2025-09-10 08:34:05] [INFO] New page being crawled: https://www.espn.com (depth: 0, source: genesis_seed)
[2025-09-10 08:34:05] [INFO] Crawled page being passed to AI Classifier: https://www.espn.com
[2025-09-10 08:34:05] [INFO] The classifier's verdict: https://www.espn.com -> probability=0.087 (NEGATIVE)
[2025-09-10 08:34:05] [INFO] Link being evaluated: https://www.espn.com/watch/ and calculated relevancy score: 1.00
[2025-09-10 08:34:05] [INFO] URL passing to final V2 verification pipeline: https://streaming-site.com (AI confidence: 0.85)
[2025-09-10 08:34:06] [INFO] URL successfully written to database: https://verified-site.com
[2025-09-10 08:35:42] [INFO] SCOUT RUN ENDING - FINAL STATISTICS
```

### Real-Time Monitoring Commands

**Monitor Live Crawling Activity**:
```bash
# Follow scout operations in real-time
tail -f signal_scout/scout.log

# Monitor AI classification decisions
tail -f signal_scout/scout.log | grep "classifier's verdict"

# Track verification pipeline activity  
tail -f signal_scout/scout.log | grep "V2 verification"

# Watch database write operations
tail -f signal_scout/scout.log | grep "successfully written to database"
```

**Log Analysis Commands**:
```bash
# View recent crawl summary
grep "FINAL OPERATIONAL METRICS" signal_scout/scout.log -A 10 | tail -11

# Analyze AI classification performance
grep "Classification result" signal_scout/scout.log | awk -F'probability' '{print $2}' | sort

# Count discovery success rate
echo "Total AI Classifications: $(grep -c "classifier's verdict" signal_scout/scout.log)"
echo "V2 Verifications Passed: $(grep -c "successfully written to database" signal_scout/scout.log)"

# Check error patterns
grep "\[ERROR\]" signal_scout/scout.log | tail -10
```

### Database Operations and Debugging

**Operational Database Queries**:
```bash
# View recent V3 discoveries
sqlite3 shared_data/sites.db "
SELECT name, url, source, confidence_score, last_verified 
FROM sites 
WHERE source LIKE '%v3%' 
ORDER BY last_verified DESC 
LIMIT 10;"

# Analyze discovery source breakdown
sqlite3 shared_data/sites.db "
SELECT source, COUNT(*) as count, AVG(confidence_score) as avg_confidence
FROM sites 
GROUP BY source 
ORDER BY count DESC;"

# Check quarantine status
sqlite3 shared_data/sites.db "
SELECT status, COUNT(*) as count 
FROM sites 
GROUP BY status;"

# View high-confidence sites
sqlite3 shared_data/sites.db "
SELECT name, url, confidence_score, last_verified
FROM sites 
WHERE confidence_score >= 70 AND is_active = 1
ORDER BY confidence_score DESC;"
```

**Database Health Monitoring**:
```bash
# Check database integrity
sqlite3 shared_data/sites.db "PRAGMA integrity_check;"

# View database size and statistics
ls -lh shared_data/sites.db
sqlite3 shared_data/sites.db "SELECT COUNT(*) as total_sites FROM sites;"

# Backup database before maintenance
cp shared_data/sites.db shared_data/sites.db.backup.$(date +%Y%m%d_%H%M%S)
```

### Performance Monitoring

**Scrapy Performance Metrics**:
```bash
# Extract Scrapy statistics from logs
grep "Dumping Scrapy stats:" signal_scout/scout.log -A 20 | tail -21

# Monitor memory usage trends
grep "Peak memory usage" signal_scout/scout.log | tail -10

# Check request/response rates
grep "pages/min" signal_scout/scout.log | tail -5
```

**System Resource Monitoring**:
```bash
# Monitor during live crawl
watch -n 5 'ps aux | grep scrapy'

# Check disk space usage
df -h . && du -sh shared_data/ signal_scout/

# Monitor network activity
netstat -i
```

### Troubleshooting Common Issues

**Issue: No URLs Being Discovered**
```bash
# Check seed URL accessibility
grep "Creating initial request" signal_scout/scout.log | head -5

# Verify AI classifier is working
grep "AI Classifier initialized" signal_scout/scout.log

# Check if sites are being filtered by AI threshold
grep "filtered out by AI classifier" signal_scout/scout.log | wc -l
```

**Issue: High Memory Usage**
```bash
# Check current Scrapy settings
grep "MEMUSAGE" signal_scout/v3_spider/settings.py

# Monitor memory during crawl
grep "memory usage" signal_scout/scout.log | tail -10
```

**Issue: Database Write Failures**
```bash
# Check database permissions
ls -la shared_data/sites.db

# Verify database schema
sqlite3 shared_data/sites.db ".schema sites"

# Check for database locks
sqlite3 shared_data/sites.db "PRAGMA integrity_check;"
```

### Log Management

**Log Rotation and Cleanup**:
```bash
# Archive old logs (run before major crawls)
mkdir -p logs/archive/
mv signal_scout/scout.log logs/archive/scout-$(date +%Y%m%d_%H%M%S).log
touch signal_scout/scout.log

# Clean up old archived logs (keep last 30 days)
find logs/archive/ -name "scout-*.log" -mtime +30 -delete
```

**Log Analysis Scripts**:
```bash
# Create a simple log analysis script
cat > analyze_crawl.sh << 'EOF'
#!/bin/bash
LOG_FILE="signal_scout/scout.log"

echo "=== SidelineSignal V3 Crawl Analysis ==="
echo "Pages Crawled: $(grep -c "New page being crawled" $LOG_FILE)"
echo "AI Classifications: $(grep -c "classifier's verdict" $LOG_FILE)"  
echo "V2 Verifications: $(grep -c "V2 verification" $LOG_FILE)"
echo "Database Writes: $(grep -c "successfully written" $LOG_FILE)"
echo "Errors: $(grep -c "\[ERROR\]" $LOG_FILE)"
echo "Last Run: $(tail -20 $LOG_FILE | grep "SCOUT RUN ENDING" | head -1)"
EOF

chmod +x analyze_crawl.sh
./analyze_crawl.sh
```

This professional logging and debugging system provides complete operational visibility into the SidelineSignal V3 cognitive crawler, enabling effective monitoring, troubleshooting, and performance optimization.