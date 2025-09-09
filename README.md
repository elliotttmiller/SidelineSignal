# SidelineSignal - Autonomous Streaming Site Monitoring System

SidelineSignal is a professional monorepo containing an autonomous streaming site monitoring system. The system consists of two main components that work together to discover, verify, and monitor streaming sites with minimal human intervention.

## Repository Structure

### `sideline_app/`
The main Flask application that provides a web interface and API for monitoring streaming sites. This application reads from the shared database to display real-time status information.

**Key Features:**
- Real-time site status monitoring with response times
- RESTful API endpoint at `/api/statuses`
- Concurrent status checking for optimal performance
- Status change logging and tracking

### `signal_scout/`
An intelligent discovery engine that autonomously finds, verifies, and manages streaming sites. The Scout runs independently and feeds the main application with verified site data.

**Key Components:**
- **scout.py**: Main orchestration engine
- **hunters.py**: URL discovery modules (Community Aggregator, Permutation Verifier)
- **verification.py**: Multi-stage verification pipeline (Probe, Content Analysis, DOM Fingerprinting)

**Key Features:**
- Automated site discovery using multiple hunting strategies
- Advanced verification with confidence scoring
- Self-healing mechanism that deactivates failing sites
- Comprehensive logging and reporting

### `shared_data/`
Contains the SQLite database (`sites.db`) that serves as the central data store for both applications. The database maintains site information, verification status, and metadata.

**Database Schema:**
- `sites` table: id, name, url, source, last_verified, confidence_score, is_active

## Getting Started

### Prerequisites
Install dependencies for each component:

```bash
# For the main application
pip install -r requirements_app.txt

# For the scout engine  
pip install -r requirements_scout.txt
```

### Running the System

1. **Start the Scout (recommended to run periodically)**:
```bash
cd signal_scout/
python scout.py
```

2. **Start the Web Application**:
```bash
cd sideline_app/
python app.py
```

The application will be available at `http://localhost:5000`

### API Usage

**GET /api/statuses** - Returns current status of all active sites with source information:
```json
[
  {
    "name": "StreamEast",
    "url": "https://streameast.app", 
    "source": "scout_discovery",
    "status": "Operational",
    "status_code": 200,
    "response_time": 342,
    "error": null
  }
]
```

## Architecture

The system follows a modular, autonomous architecture:
- **Separation of Concerns**: Discovery, verification, and monitoring are handled by specialized components
- **Shared Data Store**: Central database enables loose coupling between components
- **Self-Healing**: Automatic cleanup of failed sites maintains data quality
- **Scalable Design**: Components can be run independently and scaled as needed

## Core Protocols

1. **Unquestionable Reliability**: Robust error handling and graceful degradation
2. **User-Centric Performance**: Background processing with responsive user interface
3. **Absolute Clarity**: Clean data presentation with immediate insights
4. **Scalable & Modular Design**: Independent component development and deployment
5. **Holistic Craftsmanship**: Professional quality throughout the system