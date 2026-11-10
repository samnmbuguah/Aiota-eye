#!/usr/bin/env python3
"""
edge_sync.py: Minimal-footprint, resilient Edge-to-Cloud Sync Daemon.
Listens to Frigate MQTT events, caches payloads in local SQLite during network drops,
and pushes snapshots and clips to the Cloud Hub via authenticated endpoints.
"""

import os
import sys
import json
import time
import sqlite3
import logging
import threading
from typing import Dict, Any, Optional
import requests
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EdgeSync")

CONFIG = {
    "MQTT_HOST": os.getenv("MQTT_HOST", "127.0.0.1"),
    "MQTT_PORT": int(os.getenv("MQTT_PORT", 1883)),
    "FRIGATE_API_URL": os.getenv("FRIGATE_API_URL", "http://127.0.0.1:5000"),
    "CLOUD_API_URL": os.getenv("CLOUD_API_URL", "http://127.0.0.1:8000/api/v1"),
    "APPLIANCE_TOKEN": os.getenv("APPLIANCE_TOKEN", "default_secret_token"),
    "DB_PATH": os.getenv("QUEUE_DB_PATH", "/tmp/edge_queue.db"),
    "SYNC_INTERVAL_SEC": float(os.getenv("SYNC_INTERVAL_SEC", "2.0")),
    "MAX_RETRIES": 5,
}


class LocalQueue:
    """Persistent transactional buffer for events awaiting upload during network outages."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path, timeout=15)

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pending_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE,
                    camera TEXT,
                    label TEXT,
                    confidence REAL,
                    zones TEXT,
                    payload_json TEXT,
                    started_at REAL,
                    ended_at REAL,
                    status TEXT DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    created_at REAL
                )
                """
            )
            conn.commit()

    def enqueue(self, event_id: str, camera: str, label: str, confidence: float,
                zones: list, payload: Dict[str, Any], started_at: float, ended_at: Optional[float] = None):
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO pending_events (
                    event_id, camera, label, confidence, zones, payload_json, started_at, ended_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(event_id) DO UPDATE SET
                    ended_at = excluded.ended_at,
                    zones = excluded.zones,
                    payload_json = excluded.payload_json
                """,
                (
                    event_id,
                    camera,
                    label,
                    confidence,
                    json.dumps(zones),
                    json.dumps(payload),
                    started_at,
                    ended_at,
                    time.time(),
                ),
            )
            conn.commit()
            logger.info(f"Queued/Updated event {event_id} ({label})")

    def fetch_pending(self, limit: int = 10):
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM pending_events 
                WHERE status = 'pending' 
                ORDER BY id ASC LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def mark_completed(self, event_id: str):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM pending_events WHERE event_id = ?", (event_id,))
            conn.commit()

    def mark_failed(self, event_id: str):
        with self._get_conn() as conn:
            conn.execute(
                """
                UPDATE pending_events 
                SET retry_count = retry_count + 1,
                    status = CASE WHEN retry_count >= ? THEN 'failed' ELSE 'pending' END
                WHERE event_id = ?
                """,
                (CONFIG["MAX_RETRIES"], event_id),
            )
            conn.commit()


class EdgeSyncDaemon:
    def __init__(self, queue: LocalQueue):
        self.queue = queue
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {CONFIG['APPLIANCE_TOKEN']}",
            "User-Agent": "EdgeSyncDaemon/1.0",
        })
        self.stop_event = threading.Event()

    def fetch_frigate_snapshot(self, event_id: str) -> Optional[bytes]:
        url = f"{CONFIG['FRIGATE_API_URL']}/api/events/{event_id}/snapshot.jpg"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return resp.content
        except Exception as e:
            logger.warning(f"Failed to fetch snapshot for {event_id}: {e}")
        return None

    def fetch_frigate_clip(self, event_id: str) -> Optional[bytes]:
        url = f"{CONFIG['FRIGATE_API_URL']}/api/events/{event_id}/clip.mp4"
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                return resp.content
        except Exception as e:
            logger.debug(f"Clip not ready or failed for {event_id}: {e}")
        return None

    def push_event(self, record: Dict[str, Any]) -> bool:
        event_id = record["event_id"]
        snapshot_bytes = self.fetch_frigate_snapshot(event_id)
        clip_bytes = self.fetch_frigate_clip(event_id)

        files = {}
        if snapshot_bytes:
            files["snapshot"] = (f"{event_id}.jpg", snapshot_bytes, "image/jpeg")
        if clip_bytes:
            files["clip"] = (f"{event_id}.mp4", clip_bytes, "video/mp4")

        data = {
            "edge_event_id": event_id,
            "camera_identifier": record["camera"],
            "primary_label": record["label"],
            "confidence": record["confidence"],
            "zones_entered": record["zones"],
            "detection_payload": record["payload_json"],
            "started_at": record["started_at"],
            "ended_at": record["ended_at"],
        }

        try:
            upload_url = f"{CONFIG['CLOUD_API_URL']}/events/ingest"
            resp = self.session.post(upload_url, data=data, files=files if files else None, timeout=30)
            if resp.status_code in (200, 201):
                logger.info(f"Successfully uploaded event {event_id} to cloud")
                return True
            else:
                logger.error(f"Cloud ingestion returned HTTP {resp.status_code}: {resp.text}")
                return False
        except requests.RequestException as e:
            logger.warning(f"Network error pushing event {event_id}: {e}")
            return False

    def sync_loop(self):
        """Worker thread that drains the SQLite queue with backoff."""
        while not self.stop_event.is_set():
            pending = self.queue.fetch_pending(limit=5)
            if not pending:
                time.sleep(CONFIG["SYNC_INTERVAL_SEC"])
                continue

            for item in pending:
                success = self.push_event(item)
                if success:
                    self.queue.mark_completed(item["event_id"])
                else:
                    self.queue.mark_failed(item["event_id"])
                    time.sleep(2.0)  # Brief backoff before next attempt

            time.sleep(0.5)

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to Frigate MQTT broker")
            client.subscribe("frigate/events")
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            event_type = payload.get("type")  # 'new', 'update', 'end'
            after = payload.get("after", {})
            event_id = after.get("id")

            if not event_id:
                return

            camera = after.get("camera", "unknown")
            label = after.get("label", "unknown")
            confidence = float(after.get("top_score") or after.get("score") or 0.0)
            zones = after.get("current_zones", [])
            started_at = float(after.get("start_time", time.time()))
            ended_at = float(after.get("end_time")) if after.get("end_time") else None

            # Only queue if verified object meets minimal trigger threshold
            if confidence >= 0.5:
                self.queue.enqueue(
                    event_id=event_id,
                    camera=camera,
                    label=label,
                    confidence=confidence,
                    zones=zones,
                    payload=after,
                    started_at=started_at,
                    ended_at=ended_at,
                )
        except Exception as e:
            logger.error(f"Error parsing MQTT event message: {e}", exc_info=True)

    def run(self):
        worker = threading.Thread(target=self.sync_loop, daemon=True)
        worker.start()

        client = mqtt.Client()
        client.on_connect = self.on_mqtt_connect
        client.on_message = self.on_mqtt_message

        try:
            client.connect(CONFIG["MQTT_HOST"], CONFIG["MQTT_PORT"], 60)
            client.loop_forever()
        except KeyboardInterrupt:
            logger.info("Stopping Edge Sync daemon...")
            self.stop_event.set()
            client.disconnect()
            worker.join()


if __name__ == "__main__":
    queue_db = LocalQueue(CONFIG["DB_PATH"])
    daemon = EdgeSyncDaemon(queue_db)
    daemon.run()
