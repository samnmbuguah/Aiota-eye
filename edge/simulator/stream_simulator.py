#!/usr/bin/env python3
"""
stream_simulator.py:
Simulates an Edge NVR / Frigate appliance streaming detection events from video feeds
directly into the live cloud API (https://aiota.akilinova.co.ke/api).
Generates realistic multi-vertical events with snapshots and clips in an automated loop.
"""

import os
import sys
import time
import random
import uuid
import subprocess
import requests

CLOUD_API_URL = os.getenv("CLOUD_API_URL", "https://aiota.akilinova.co.ke/api")
APPLIANCE_TOKEN = os.getenv("APPLIANCE_TOKEN", "akilinova_edge_secret_token_12345")
WORKDIR = "/tmp/aiota_sim"
os.makedirs(WORKDIR, exist_ok=True)

# Synthetic event scenarios covering agricultural, industrial, and security verticals
SCENARIOS = [
    {
        "camera_identifier": "cam_gate_01",
        "camera_name": "North Perimeter Gate",
        "primary_label": "coyote",
        "confidence_range": (0.82, 0.96),
        "zones": ["gate_perimeter", "fence_line"],
        "bbox": [150, 200, 310, 420],
        "vertical": "livestock_predator",
    },
    {
        "camera_identifier": "cam_feedlot_02",
        "camera_name": "Livestock Feedlot",
        "primary_label": "cow",
        "confidence_range": (0.88, 0.99),
        "zones": ["feeding_trough"],
        "bbox": [80, 120, 480, 560],
        "vertical": "livestock_health",
    },
    {
        "camera_identifier": "cam_gate_01",
        "camera_name": "North Perimeter Gate",
        "primary_label": "intruder person",
        "confidence_range": (0.85, 0.95),
        "zones": ["restricted_entrance"],
        "bbox": [210, 100, 450, 320],
        "vertical": "security_perimeter",
    },
    {
        "camera_identifier": "cam_feedlot_02",
        "camera_name": "Livestock Feedlot",
        "primary_label": "tractor vehicle",
        "confidence_range": (0.90, 0.98),
        "zones": ["driveway", "equipment_depot"],
        "bbox": [50, 80, 520, 600],
        "vertical": "farm_logistics",
    },
    {
        "camera_identifier": "cam_gate_01",
        "camera_name": "North Perimeter Gate",
        "primary_label": "stray dog",
        "confidence_range": (0.78, 0.92),
        "zones": ["fence_line"],
        "bbox": [180, 240, 320, 400],
        "vertical": "perimeter_warning",
    },
]


def generate_synthetic_media(event_id: str, label: str, camera: str) -> tuple[str, str]:
    """Generates a branded synthetic 3-second MP4 clip and a JPEG snapshot via ffmpeg."""
    clip_path = os.path.join(WORKDIR, f"{event_id}.mp4")
    snap_path = os.path.join(WORKDIR, f"{event_id}.jpg")

    clean_label = label.replace(" ", "_").upper()
    ff_cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", "testsrc=duration=3:size=640x360:rate=15",
        "-vf", f"drawtext=text='CAM_STREAM_ACTIVE_{clean_label}':fontcolor=white:fontsize=20:box=1:boxcolor=black@0.6:x=30:y=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        clip_path
    ]
    subprocess.run(ff_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Extract snapshot
    ff_snap = [
        "ffmpeg", "-y", "-ss", "00:00:01",
        "-i", clip_path, "-vframes", "1", "-q:v", "2",
        snap_path
    ]
    subprocess.run(ff_snap, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    return snap_path, clip_path


def send_simulated_detection(scenario: dict) -> bool:
    event_id = f"evt_sim_{uuid.uuid4().hex[:8]}"
    label = scenario["primary_label"]
    camera = scenario["camera_name"]
    cam_id = scenario["camera_identifier"]
    confidence = round(random.uniform(*scenario["confidence_range"]), 2)
    zones = scenario["zones"]

    print(f"\n[Simulator] >>> Triggering: {label.upper()} on {camera} (conf: {confidence*100:.0f}%)")
    snap_file, clip_file = generate_synthetic_media(event_id, label, camera)

    upload_url = f"{CLOUD_API_URL}/events/ingest"
    headers = {"Authorization": f"Bearer {APPLIANCE_TOKEN}"}

    data = {
        "edge_event_id": event_id,
        "camera_identifier": cam_id,
        "primary_label": label,
        "confidence": confidence,
        "zones_entered": str(zones).replace("'", '"'),
        "detection_payload": str({"bbox": scenario["bbox"], "scenario": scenario["vertical"]}).replace("'", '"'),
        "started_at": time.time() - 3.0,
        "ended_at": time.time(),
    }

    with open(snap_file, "rb") as s_f, open(clip_file, "rb") as c_f:
        files = {
            "snapshot": (f"{event_id}.jpg", s_f, "image/jpeg"),
            "clip": (f"{event_id}.mp4", c_f, "video/mp4"),
        }
        try:
            resp = requests.post(upload_url, data=data, files=files, headers=headers, timeout=15)
            if resp.status_code in (200, 201):
                res = resp.json()
                print(f"[Simulator] [OK] Successfully uploaded {event_id} | Qdrant Indexed: {res.get('indexed')}")
                return True
            else:
                print(f"[Simulator] [FAIL] Server rejected: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            print(f"[Simulator] [ERROR] Upload failed: {e}")
            return False
        finally:
            # Clean up local temporary media
            if os.path.exists(snap_file):
                os.remove(snap_file)
            if os.path.exists(clip_file):
                os.remove(clip_file)


def run_loop(count: int = 5, delay: float = 3.0):
    print(f"============================================================")
    print(f" Aiota Edge Simulator: Streaming to {CLOUD_API_URL}")
    print(f" Ingesting {count} simulated video detections into Qdrant Cloud...")
    print(f"============================================================")

    for i in range(count):
        scenario = random.choice(SCENARIOS)
        send_simulated_detection(scenario)
        if i < count - 1:
            time.sleep(delay)

    print("\n[Simulator] Completed batch simulation. Visit https://aiota.akilinova.co.ke to search!")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    run_loop(count=count)
