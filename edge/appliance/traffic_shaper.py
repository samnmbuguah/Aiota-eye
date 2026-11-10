#!/usr/bin/env python3
"""
traffic_shaper.py: Low-Bandwidth Cellular & Metred Network Optimizer for Kenya.
Ensures the appliance never saturates remote Safaricom / Airtel 4G connections.
Enforces bandwidth caps, off-peak night scheduling, and token-bucket rate limiting.
"""

import time
import os
import threading
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Shaper] %(message)s")
logger = logging.getLogger("TrafficShaper")


class CellularTrafficShaper:
    """
    Token-bucket rate limiter that enforces strict upstream bandwidth limits (e.g. 50 KB/s)
    and optional off-peak high-bandwidth sync windows (e.g. midnight to 5 AM).
    """

    def __init__(
        self,
        max_rate_kbps: int = 50,          # Standard daytime limit (50 KB/s ~ 400 kbps)
        burst_multiplier: float = 1.5,
        off_peak_start_hour: int = 0,     # Midnight
        off_peak_end_hour: int = 5,       # 5:00 AM (cheap Safaricom night data bundles)
        off_peak_multiplier: float = 4.0  # 4x higher bandwidth during off-peak hours
    ):
        self.base_bytes_per_sec = max_rate_kbps * 1024
        self.burst_capacity = self.base_bytes_per_sec * burst_multiplier
        self.tokens = self.burst_capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()

        self.off_peak_start = off_peak_start_hour
        self.off_peak_end = off_peak_end_hour
        self.off_peak_mult = off_peak_multiplier

    def is_off_peak(self) -> bool:
        current_hour = datetime.now().hour
        if self.off_peak_start <= self.off_peak_end:
            return self.off_peak_start <= current_hour < self.off_peak_end
        else:
            return current_hour >= self.off_peak_start or current_hour < self.off_peak_end

    def current_allowed_rate(self) -> float:
        rate = self.base_bytes_per_sec
        if self.is_off_peak():
            rate *= self.off_peak_mult
        return rate

    def acquire(self, byte_count: int, max_wait: float = 10.0) -> bool:
        """Blocks until sufficient bandwidth tokens are available, or timeouts."""
        start_time = time.time()

        while True:
            with self.lock:
                now = time.time()
                elapsed = now - self.last_refill
                rate = self.current_allowed_rate()

                # Refill tokens based on elapsed time and current rate
                self.tokens = min(self.burst_capacity, self.tokens + elapsed * rate)
                self.last_refill = now

                if self.tokens >= byte_count:
                    self.tokens -= byte_count
                    return True

                deficit = byte_count - self.tokens
                sleep_needed = deficit / rate

            if time.time() - start_time + sleep_needed > max_wait:
                logger.warning(f"Bandwidth cap exceeded. Throttling transfer of {byte_count} bytes.")
                return False

            time.sleep(min(sleep_needed, 0.5))

    def wrap_file_stream(self, file_path: str, chunk_size: int = 8192):
        """Yields chunks of a video file while conforming to bandwidth throttling."""
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                self.acquire(len(chunk))
                yield chunk
