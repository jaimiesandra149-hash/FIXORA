# FIXORA Backend

Intelligent diagnostic and troubleshooting REST API built with FastAPI and Uvicorn.

## Features
- **Query Enrichment**: Multi-keyword confidence scoring and symptom/trigger extraction.
- **Hardware vs Software Risk**: Automatic detection of OLED green line, battery swelling, water ingress, or software glitches.
- **Comprehensive Action Catalog**: Covering Performance, Battery, Display, Connectivity, Audio, Camera, Charging/Moisture, Overheating, and Recovery.
- **Stateful Guided Sessions**: Interactive forward/backward/skip step tracking, execution history, and resolution metrics.
- **CORS Support**: Configured for Vite and modern web clients.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server on port 8000
uvicorn app:app --reload --port 8000
```
