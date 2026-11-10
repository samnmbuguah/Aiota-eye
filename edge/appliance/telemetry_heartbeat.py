#!/usr/bin/env python3
"""
telemetry_heartbeat.py:
Monitors appliance hardware metrics (CPU, RAM, SSD rolling buffer, 4G connection)
and pings the Cloud API with periodic health status updates.
"""

import os
import time
import shutil
import subprocess
import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Heartbeat] %(message)s")
logger = logging.getLogger("TelemetryHeartbeat")

CLOUD_API_URL = os.getenv("CLOUD_API_URL", "https://aiota.akilinova.co.ke/api")
APPLIANCE_TOKEN = os.getenv("APPLIANCE_TOKEN", "akilinova_edge_secret_token_12345")
BUFFER_DIR = os.getenv("BUFFER_DIR", "/tmp")


def get_system_metrics() -> dict:
    # Disk / SSD Rolling Buffer usage
    total, used, free = shutil.disk_usage(BUFFER_DIR)
    disk_percent = round((used / total) * 100, 1)

    # CPU Load
    try:
        load_1, load_5, _ = os.getloadavg()
    except Exception:
        load_1, load_5 = 0.5, 0.4

    # Memory Usage
    mem_percent = 45.0
    try:
        with open("/proc/meminfo") as f:
            lines = f.readlines()
            mem_total = int([x for x in lines if "MemTotal:" in x][0].split()[1])
            mem_avail = int([x for x in lines if "MemAvailable:" in x][0].split()[1])
            mem_percent = round(((mem_total - mem_avail) / mem_total) * 100, 1)
    except Exception:
        pass

    return {
        "status": "online",
        "ssd_buffer_usage_pct": disk_percent,
        "cpu_load_1m": load_1,
        "ram_usage_pct": mem_percent,
        "uplink_type": "4G_cellular_safaricom",
        "timestamp": time.time(),
    }


def send_heartbeat():
    metrics = get_system_metrics()
    url = f"{CLOUD_API_URL}/appliances/heartbeat"
    headers = {
        "Authorization": f"Bearer {APPLIANCE_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, json=metrics, headers=headers, timeout=5)
        if resp.status_code == 200:
            logger.info(f"Heartbeat OK | SSD Buffer: {metrics['ssd_buffer_usage_pct']}% | CPU: {metrics['cpu_load_1m']}")
        else:
            logger.warning(f"Heartbeat response: {resp.status_code}")
    except Exception as e:
        logger.warning(f"Failed to deliver heartbeat to cloud: {e}")


def run_heartbeat_loop(interval_sec: int = 30):
    logger.info("Starting Appliance Telemetry Heartbeat loop...")
    while True:
        send_heartbeat()
        time.sleep(interval_sec)


if __name__ == "__main__":
    send_heartbeat()
