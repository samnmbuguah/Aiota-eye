# Aiota Box — Physical Appliance Installation Guide

This guide describes how to assemble, install, and configure an **Aiota Box** on-premise at a client facility (e.g. farm, warehouse, manufacturing plant, or retail shop).

---

## 1. Hardware Specifications (BOM)

The reference appliance is an energy-efficient, fanless or ultra-quiet Mini-PC:

| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **Processor** | Intel Alder Lake-N N100 (4 cores, up to 3.4GHz) | Intel Core i3-N305 or Core i5-1240P |
| **RAM** | 16 GB DDR5 4800MHz SO-DIMM | 32 GB DDR5 |
| **Primary Storage** | 512 GB M.2 NVMe PCIe 3.0 SSD | 1 TB NVMe SSD (Gen4) |
| **Networking** | Dual 2.5GbE Intel i225/i226 Ethernet Ports | Dual 2.5GbE LAN + 4G LTE M.2 Slot |
| **Video Acceleration** | Intel UHD Graphics (VA-API / OpenVINO supported)| Intel UHD 24/32 EUs |
| **Power Consumption** | ~6W Idle, ~18W Full AI Load | 15–25W Under Load |

---

## 2. Network Topology & Physical Cabling

```
                      [Safaricom / Airtel 4G Router]
                                     |
                                     v (WAN / Internet)
                            [eth0: DHCP / 4G Uplink]
                           +------------------------+
                           |       AIOTA BOX        |
                           |   (Intel N100 Mini-PC) |
                           +------------------------+
                            [eth1: 192.168.10.1/24]
                                     | (Isolated Camera LAN)
                                     v
                        [Gigabit PoE Network Switch]
                         |           |           |
                         v           v           v
                     [CAM 01]    [CAM 02]    [CAM 03]
```

* **Interface `eth0` (WAN Uplink)**: Connected to the site's internet router (Safaricom 4G Wi-Fi router, fiber ONT, or Starlink). Configured via DHCP.
* **Interface `eth1` (Camera LAN)**: Connected to a dedicated PoE switch powering the IP cameras. The Aiota Box serves as DHCP server on `192.168.10.0/24`, isolating camera traffic from the corporate office LAN.

---

## 3. Base OS Installation

1. Install **Ubuntu Server 24.04 LTS (64-bit)** using a bootable USB drive.
2. During setup:
   * Hostname: `aiota-box-<site-name>` (e.g., `aiota-box-naivasha-01`)
   * Username: `aiota`
   * Enable **Install OpenSSH Server**.
3. Verify Intel GPU acceleration drivers:
   ```bash
   sudo apt update && sudo apt install -y vainfo intel-media-va-driver-non-free docker.io docker-compose-v2
   sudo usermod -aG docker,video,render aiota
   vainfo # Should report VAProfileH264Main, VAProfileH264High, VAProfileHEVCMain
   ```

---

## 4. Software Deployment

### 4.1. Clone Repository & Prepare Directories
```bash
sudo mkdir -p /etc/aiota /data/frigate/storage
sudo chown -R aiota:aiota /etc/aiota /data/frigate

git clone git@github.com:samnmbuguah/Aiota-eye.git /opt/aiota
cd /opt/aiota/edge/appliance
```

### 4.2. Configure Frigate & ONVIF Discovery
Create `/etc/aiota/config.yml`:
```yaml
mqtt:
  host: 127.0.0.1
  port: 1883

detectors:
  ov:
    type: openvino
    device: GPU # Uses Intel UHD Graphics for zero CPU impact

cameras:
  gate_main:
    ffmpeg:
      inputs:
        - path: rtsp://admin:Security2026@192.168.10.21:554/Streaming/Channels/101
          roles:
            - record
        - path: rtsp://admin:Security2026@192.168.10.21:554/Streaming/Channels/102
          roles:
            - detect
    detect:
      width: 1280
      height: 720
      fps: 5
    objects:
      track:
        - person
        - car
        - truck
        - motorcycle
```

### 4.3. Launch Container Stack
```bash
docker compose -f /opt/aiota/edge/appliance/docker-compose.edge.yml up -d
```

---

## 5. Automated Systemd Service Configuration

Ensure the Aiota appliance auto-starts on boot and power recovery:

```bash
sudo systemctl enable docker
sudo tee /etc/systemd/system/aiota-edge.service > /dev/null <<EOF
[Unit]
Description=Aiota Edge Intelligence Appliance
After=docker.service network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/aiota/edge/appliance
ExecStart=/usr/bin/docker compose -f docker-compose.edge.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.edge.yml down

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable aiota-edge.service
```

---

## 6. Verification & Commissioning Checklist

- [ ] `docker ps` confirms all 3 containers are healthy (`aiota_mqtt`, `aiota_frigate`, `aiota_appliance`).
- [ ] Local web interface accessible at `http://<box-ip>:5000`.
- [ ] Telemetry heartbeat confirmed in cloud hub console ([https://aiota.akilinova.co.ke/console](https://aiota.akilinova.co.ke/console)).
- [ ] Daytime bandwidth capped at 50 KB/s on `eth0`.
- [ ] Motion events appear in the cloud 24-hour event timeline.
