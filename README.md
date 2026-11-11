# Aiota — Edge-First Video Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Cloud_Vector_DB-red.svg)](https://qdrant.tech/)
[![Frigate](https://img.shields.io/badge/Frigate-NVR_OpenVINO-orange.svg)](https://frigate.video/)
[![License](https://img.shields.io/badge/License-Proprietary-black.svg)]()

> **Spot AI-inspired, edge-first neural surveillance and video intelligence built specifically for high-latency, bandwidth-constrained emerging markets (Kenya, East Africa).**

---

## 🌐 Live Production Endpoints

* **Enterprise Marketing Page**: [https://aiota.akilinova.co.ke/](https://aiota.akilinova.co.ke/)
* **Enterprise Command Console**: [https://aiota.akilinova.co.ke/console](https://aiota.akilinova.co.ke/console)
* **Authentication Portal**: [https://aiota.akilinova.co.ke/login](https://aiota.akilinova.co.ke/login)
* **Interactive API Documentation**: [https://aiota.akilinova.co.ke/api/docs](https://aiota.akilinova.co.ke/api/docs)
* **Vector Index**: Qdrant Cloud (`detection_events_clip` cluster)

---

## 🎯 The Core Philosophy: Edge-First Intelligence

Traditional cloud CCTV platforms (Verkada, Cisco Meraki) stream continuous 24/7 video from every camera directly into the cloud. In Kenya and East Africa, where commercial facilities rely on **Safaricom / Airtel 4G LTE** or fixed wireless, streaming 16 high-definition cameras requires ~64 Mbps upstream and consumes over **15,000 GB per month** — incurring crippling cellular data bills and failing whenever the mobile link drops.

**Aiota solves this through a local Edge-First architecture:**
1. **The "Aiota Box" (On-Premises N100 Appliance)** sits on the local LAN with standard ONVIF/RTSP IP cameras (Hikvision, Dahua, Axis, Uniview).
2. **Local AI Inference**: Continuous video is processed in-memory at the edge using Frigate and Intel OpenVINO. 
3. **Micro-Payload Sync**: Only metadata, 384-dimensional semantic embeddings, and discrete 5-second incident clips are uploaded to the cloud hub.
4. **Bandwidth Shaping**: Uploads are restricted to **50 KB/s** during peak business hours, while heavier incident clip archives sync automatically during off-peak night hours (00:00 – 05:00 EAT) on cheap midnight bundles.
5. **Zero-Bloat Storage**: 24/7 continuous video is never stored on the cloud VM. The cloud hub maintains a lean metadata and vector index, streaming live feeds on-demand only when an authorized operator views the console.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph OnPrem["Customer Site (Farm / Warehouse / Retail)"]
        CAM1["IP Camera 1 (RTSP)"] -->|H.264/H.265| BOX["Aiota Box (Intel N100)"]
        CAM2["IP Camera 2 (ONVIF)"] -->|H.264/H.265| BOX
        CAM3["IP Camera 3 (RTSP)"] -->|H.264/H.265| BOX
        
        subgraph BoxInternals["Aiota Box Software Stack"]
            ONVIF["ONVIF Auto-Discovery"] --> FRIG["Frigate NVR + OpenVINO"]
            FRIG -->|MQTT Event Bus| SYNC["Aiota Edge Sync Daemon"]
            FRIG -->|Local Restream| G2R["go2rtc (WebRTC / HLS)"]
            SYNC -->|Daytime: 50 KB/s Cap<br>Night: Bulk Sync| SHAPER["Adaptive Traffic Shaper"]
        end
        BOX --- BoxInternals
    end

    subgraph CellularUplink["Safaricom / Airtel 4G LTE"]
        SHAPER -->|HTTPS / REST API| CLOUD
    end

    subgraph CloudHub["Aiota Cloud Intelligence Hub (Nairobi / Cloud)"]
        CLOUD["Django Ninja Cloud API"]
        DB[("PostgreSQL / SQLite<br>Relational State")]
        QDRANT[("Qdrant Cloud<br>Neural Vector Index")]
        MEDIA["Media Vault<br>(5s Event Clips & Snaps)"]
        
        CLOUD --> DB
        CLOUD --> QDRANT
        CLOUD --> MEDIA
    end

    subgraph ClientBrowsers["Operator Dashboards & Wall Displays"]
        ADMIN["Security Operations Console"]
        MOBILE["Mobile Manager (WhatsApp Alerts)"]
        
        ADMIN <-->|Search & Analytics| CLOUD
        ADMIN <-->|Live Stream On-Demand| G2R
        CLOUD -->|Instant Dispatch| MOBILE
    end
```

---

## ⚡ Key Capabilities

### 1. Neural Natural Language Video Search
Instead of scrubbing through 24 hours of timeline scrubbers, operators search using conversational phrases:
* `"White Toyota Hilux entering loading dock"`
* `"Horses grazing near perimeter fence"`
* `"Queue forming at checkout cashier till"`
* `"Pedestrian crossing junction with bicycle"`

Searches are mapped to vector embeddings and queried against **Qdrant Cloud** in under 50 milliseconds, returning verified event clips and timestamps instantly.

### 2. Multi-Mode Live Camera Wall
The cloud console features a dynamic multi-tile surveillance wall supporting:
* **Demo CCTV Surveillance Loops**: Pre-loaded authentic security footage for pilot demonstrations.
* **Public 24/7 Live HLS Streams**: Real-time traffic and municipal cameras streamed via `Hls.js`.
* **Live On-Demand WebRTC**: Zero-latency peer-to-peer streaming directly from the on-prem Aiota Box.
* **Custom Feed Tester**: Test external streams (e.g., smartphone *IP Webcam*, HLS `.m3u8`, or HTTP feeds) in real time.

### 3. Automated WhatsApp & SMS Alert Rules
Configure conditional trigger rules (e.g. `confidence >= 0.85`, `zone = "North_Gate"`, `label = "vehicle"` after 10 PM) that immediately dispatch WhatsApp alerts with event snapshot links to site managers.

### 4. Zero-Bloat Storage Engine
* Continuous 24/7 recordings are kept on local NVMe ring buffers at the edge.
* The cloud hub stores **only discrete event assets** (5-second MP4 clips under 1 MB, JPEG snapshots under 150 KB).
* Automated 24-hour / 7-day rolling pruning prevents disk bloat on both edge and cloud nodes.

---

## 📁 Repository Layout

```
Aiota/
├── README.md                      # Project overview and master guide
├── docs/                          # Detailed architecture and operational guides
│   ├── ARCHITECTURE.md            # In-depth system design & network protocols
│   ├── EDGE_SETUP.md              # Physical N100 hardware & appliance setup
│   ├── API_REFERENCE.md           # OpenAPI REST schemas and curl examples
│   └── DEMO_GUIDE.md              # Field demo instructions & stream testing
├── edge/                          # On-premises edge appliance stack
│   ├── appliance/                 # Dockerized edge daemon & discovery
│   │   ├── Dockerfile             # Edge appliance container definition
│   │   ├── docker-compose.edge.yml# Edge stack (Mosquitto + Frigate + Aiota Sync)
│   │   ├── onvif_discovery.py     # Subnet WS-Discovery probe for cameras
│   │   ├── traffic_shaper.py      # Adaptive token-bucket 4G rate limiter
│   │   ├── telemetry_heartbeat.py # Health, CPU, RAM, and SSD reporting
│   │   └── requirements.txt       # Python edge dependencies
│   ├── simulator/                 # Synthetic camera & event simulator
│   │   └── stream_simulator.py    # Local test stream generator
│   └── demo_media/                # Verified authentic CCTV benchmark clips
│       ├── clip_highway_traffic.mp4
│       ├── clip_bikes_pedestrians.mp4
│       ├── clip_farm_livestock.mp4
│       ├── clip_retail_checkout.mp4
│       └── clip_parking_movement.mp4
├── cloud/                         # Central intelligence hub (Django + Ninja)
│   └── hub/
│       ├── core/                  # Data models (Site, Camera, Event, AlertRule)
│       │   └── models.py
│       ├── api/                   # REST API routes & Qdrant vector indexing
│       │   └── endpoints.py
│       ├── tasks/                 # Async vector pipelines & maintenance
│       │   └── vector_pipeline.py
│       ├── marketing.py           # Enterprise marketing landing page
│       ├── urls.py                # URL router & Console dashboard view
│       └── settings.py            # Django cloud settings
└── frontend/                      # Standalone React/TSX dashboard components
    └── dashboard.tsx
```

---

## 🚀 Quickstart: Local Development

### Prerequisites
* Python 3.11+
* Docker & Docker Compose (optional for edge services)
* Git

### 1. Clone & Set Up Virtualenv
```bash
git clone git@github.com:samnmbuguah/Aiota-eye.git
cd Aiota-eye

python3 -m venv venv
source venv/bin/activate
pip install -r edge/appliance/requirements.txt
pip install django django-ninja qdrant-client requests
```

### 2. Configure Environment Variables
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=aiota_local_development_secret_key_2026
ALLOWED_HOSTS=localhost,127.0.0.1,aiota.akilinova.co.ke

# Qdrant Cloud Cluster
QDRANT_URL=https://e2a8ca0e-e4da-465b-8485-eb24b83d768f.us-central1-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key_here

# Appliance Master Token
APPLIANCE_MASTER_TOKEN=akilinova_edge_secret_token_12345
```

### 3. Run Migrations & Start Hub Server
```bash
python3 cloud/hub/manage.py migrate
python3 cloud/hub/manage.py runserver 0.0.0.0:8000
```
Open [http://localhost:8000/](http://localhost:8000/) for the landing page or [http://localhost:8000/console](http://localhost:8000/console) for the enterprise console.

---

## 📡 Physical Edge Appliance Deployment

To turn an Intel N100 Mini-PC into an active **Aiota Box**:

```bash
# 1. On the N100 appliance, clone the repo
git clone git@github.com:samnmbuguah/Aiota-eye.git /opt/aiota
cd /opt/aiota/edge/appliance

# 2. Launch the containerized edge stack
docker compose -f docker-compose.edge.yml up -d

# 3. Verify services
docker ps
# Containers running:
# - aiota_frigate    (Port 5000: WebUI, 8554: RTSP, 8555: WebRTC)
# - aiota_mqtt       (Port 1883: Mosquitto)
# - aiota_appliance  (Host networking: ONVIF discovery & cloud sync)
```

Refer to [docs/EDGE_SETUP.md](docs/EDGE_SETUP.md) for full physical wiring, static IP assignments, and 4G gateway configurations.

---

## 🔍 API Testing & Quick Curl Examples

### Health Check
```bash
curl -s https://aiota.akilinova.co.ke/api/health | jq .
```

### Natural Language Neural Vector Search
```bash
curl -s -X POST https://aiota.akilinova.co.ke/api/search \
  -H "Content-Type: application/json" \
  -d '{"query_text": "white pickup truck moving in yard", "limit": 5}' | jq .
```

### Edge Event Ingestion (Multipart Form)
```bash
curl -X POST https://aiota.akilinova.co.ke/api/events/ingest \
  -H "Authorization: Bearer akilinova_edge_secret_token_12345" \
  -F "edge_event_id=evt_001" \
  -F "camera_identifier=cam_gate_01" \
  -F "primary_label=vehicle" \
  -F "confidence=0.92" \
  -F "zones_entered=[\"Entry_Gate\"]" \
  -F "started_at=$(date +%s)" \
  -F "snapshot=@edge/demo_media/snap_highway_traffic.jpg" \
  -F "clip=@edge/demo_media/clip_highway_traffic.mp4"
```

---

## 📚 Further Documentation

* [System Architecture Specification](docs/ARCHITECTURE.md)
* [Physical Edge Appliance Installation Guide](docs/EDGE_SETUP.md)
* [Full REST API Reference](docs/API_REFERENCE.md)
* [Field Demonstration & Stream Testing Guide](docs/DEMO_GUIDE.md)

---

## 📄 License & Proprietary Notice

Copyright © 2026 Akilinova Technologies Ltd. All rights reserved.  
Unauthorized distribution, copying, or reverse engineering of this software or its edge appliances is strictly prohibited.
