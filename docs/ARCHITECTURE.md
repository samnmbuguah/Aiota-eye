# Aiota System Architecture & Technical Specification

## 1. Overview & Spot AI Hybrid Topology

Aiota employs a hybrid edge-cloud video intelligence topology specifically engineered for bandwidth-constrained, high-latency environments (such as agricultural farms in Naivasha, warehouses along Mombasa Road, and retail chains across Nairobi).

Traditional cloud NVR systems attempt to pipe high-definition video directly to the cloud. For a site with 16 1080p cameras, this demands ~64 Mbps continuous upstream bandwidth—consuming upwards of 15,000 GB per month. Over commercial 4G cellular links in Kenya, this approach is both financially and technically prohibitive.

Aiota splits the intelligence pipeline into two discrete tiers:
1. **The Edge Tier ("Aiota Box")**: Operates on-premises on the local camera LAN. Captures, decodes, runs computer vision inference, buffers high-resolution footage locally, and generates compact semantic metadata.
2. **The Cloud Tier ("Aiota Hub")**: Operates centrally. Aggregates metadata, indexes multi-modal embeddings in Qdrant Vector Cloud, facilitates natural language search, manages alert rules, and proxies live video on-demand to web consoles.

```mermaid
graph TD
    subgraph LAN["On-Premises Local Area Network"]
        CAM1["Hikvision / Dahua CAM 1"] -->|RTSP H.264/H.265| EDGE["Aiota Box (Intel N100)"]
        CAM2["ONVIF Compatible CAM 2"] -->|RTSP H.264/H.265| EDGE
        CAM3["Axis / Uniview CAM 3"] -->|RTSP H.264/H.265| EDGE
        
        subgraph BoxCore["Aiota Box Runtime"]
            FRIG["Frigate NVR (OpenVINO)"]
            MOSQ["Mosquitto MQTT Broker"]
            GO2R["go2rtc Stream Gateway"]
            DISC["WS-Discovery Daemon"]
            SYNC["Edge Sync Daemon"]
            SHAPER["Bandwidth Shaper"]
            
            DISC -.->|Discovers IP| FRIG
            FRIG -->|Publishes Events| MOSQ
            FRIG -->|Feeds RTSP| GO2R
            MOSQ -->|Subscribes| SYNC
            SYNC --> SHAPER
        end
        EDGE --- BoxCore
    end

    subgraph WAN["4G LTE Cellular Gateway"]
        SHAPER -->|HTTPS / REST| API["Aiota Cloud API"]
        GO2R -.->|WebRTC / WHEP on Request| OPERATOR["Web Browser Console"]
    end

    subgraph CLOUD["Aiota Cloud Hub"]
        API --> DB[("SQLite / PostgreSQL<br>Relational Metadata")]
        API --> QDRANT[("Qdrant Cloud<br>Vector Search")]
        API --> MEDIA["Media Storage<br>(5s Clips & Snaps)"]
    end
```

---

## 2. Bandwidth Budgeting & Traffic Shaping

To operate reliably on Safaricom 4G / Airtel LTE connections:
* **Daytime Budget (06:00 – 23:59 EAT)**: Upload speed is strictly throttled to **50 KB/s**. The appliance transmits only lightweight JSON event payloads and compressed JPEG snapshots (<100 KB).
* **Nighttime Window (00:00 – 05:00 EAT)**: The traffic shaper automatically opens up to 5 MB/s to synchronize 5-second MP4 incident clips accumulated in the local NVMe buffer, capitalizing on low-cost night data bundles.

```python
# Rate limiter implementation logic (traffic_shaper.py)
class AdaptiveBandwidthShaper:
    def __init__(self, daytime_cap_kbps=50, night_cap_kbps=5000):
        self.daytime_cap = daytime_cap_kbps * 1024
        self.night_cap = night_cap_kbps * 1024

    def get_current_budget_bytes_per_sec(self):
        eat_hour = (datetime.now(timezone.utc).hour + 3) % 24
        if 0 <= eat_hour < 5:
            return self.night_cap # 5 MB/s night sync
        return self.daytime_cap   # 50 KB/s daytime cap
```

---

## 3. Streaming Architecture (Browser RTSP Gateway)

Web browsers (Chrome, Edge, Safari, Firefox) cannot directly play RTSP streams. Aiota bridges this via an integrated gateway architecture:

1. **Local RTSP Ingestion**: Cameras stream RTSP on port 554 (`rtsp://user:pass@192.168.1.100:554/stream1`).
2. **On-Demand Transcoding**: The edge `go2rtc` daemon converts the stream to **WebRTC (WHEP)** or **low-latency HLS** (`.m3u8`).
3. **P2P Streaming**: Video is transmitted directly from the edge appliance to the operator's browser session only when the camera tile is actively visible, avoiding 24/7 cloud bandwidth consumption.
4. **HLS Fallback**: For external streams or public cameras, the web console uses `Hls.js` to render HLS manifests seamlessly inside standard HTML5 `<video>` tags.

---

## 4. Vector Search Pipeline & Qdrant Integration

Aiota delivers semantic natural language video search across all connected sites:

1. **Edge Extraction**: The computer vision model extracts object classes, bounding boxes, dwell time, and zone movement.
2. **Vector Embedding**: Semantic descriptions (e.g., `"White pickup truck entering main gate loading bay"`) are transformed into a normalized 384/512-dimensional vector.
3. **Qdrant Indexing**: Vectors are upserted into the Qdrant Cloud collection `detection_events_clip` with indexed payload fields (`site_id`, `camera_id`, `confidence`, `started_at`).
4. **Cosine Similarity Querying**: When an operator enters a natural language query in the console, the hub vectorizes the text and performs an approximate nearest neighbor (ANN) search via HNSW in Qdrant, retrieving matching events in <50ms.

---

## 5. Zero-Bloat Storage & Rolling Retention

To guarantee that VM and edge appliance disks never fill up:
* **No Continuous Cloud Video**: Continuous 24/7 video recordings are never saved to the cloud VM.
* **Discrete Event Clips**: Only verified detection events generate a video asset (strictly capped at 5 seconds, under 1 MB).
* **Automated TTL Pruning**: A rolling retention worker prunes video clips older than 7 days (or 24 hours in trial/demo tiers), preserving metadata and vector points indefinitely while maintaining a fixed media disk footprint under 100 MB.
