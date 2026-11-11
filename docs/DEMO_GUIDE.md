# Aiota Demonstration & Field Pilot Guide

This document provides a step-by-step walkthrough for demonstrating Aiota to potential clients, investors, and security directors.

---

## 1. Demo Objectives & Narrative

When demonstrating Aiota in Kenya (or any emerging market), structure the conversation around three core pain points:
1. **The 4G Bandwidth Crisis**: Traditional cloud cameras consume ~15,000 GB/month for 16 cameras. Aiota consumes **under 5 GB/month** by performing AI at the edge.
2. **Finding Needles in Haystacks**: Finding an incident in 24 hours of CCTV video usually takes hours of scrubbing. With Aiota, operators type natural English phrases like `"white pickup truck"` and find the exact 5-second clip in under 1 second.
3. **Turnkey Appliance ("Aiota Box")**: Customers do **not** need to discard their existing cameras. The Aiota Box plugs directly into existing Hikvision, Dahua, Axis, or Uniview systems.

---

## 2. Navigating the Live Demo Environment

* **Production URL**: [https://aiota.akilinova.co.ke/](https://aiota.akilinova.co.ke/)
* **Console URL**: [https://aiota.akilinova.co.ke/console](https://aiota.akilinova.co.ke/console)
* **Demo Credentials**:
  * Username: `admin`
  * Password: `Admin@Akilinova2026!`

---

## 3. Step-by-Step Demonstration Script

### Step 1: The Enterprise Landing Page
1. Open [https://aiota.akilinova.co.ke/](https://aiota.akilinova.co.ke/).
2. Highlight the **"Bandwidth Economics"** calculator:
   * 16 Standard Cloud Cameras: ~64 Mbps upstream, 15,360 GB/month.
   * 16 Aiota Box Cameras: Under 0.05 Mbps upstream, 4.2 GB/month.
3. Show the Kenyan Verticals (Naivasha flower farms, Mombasa Road freight logistics, Westlands construction sites, retail stores).

### Step 2: The Multi-Camera Surveillance Wall
1. Click **"Launch Enterprise Console"** or navigate to `/console`.
2. Present the 4-camera live wall displaying:
   * **CAM-01**: Mombasa Road Highway Access
   * **CAM-02**: Commercial Turnstile & Crosswalk
   * **CAM-03**: Naivasha Flower Ranch Pasture
   * **CAM-04**: Retail Store & Forecourt Till
3. Explain the Preset Controls at the top right:
   * **`[Demo CCTV Loops]`**: Uses authentic security footage benchmarks.
   * **`[Public Live Streams]`**: Switches to active 24/7 live internet feeds via `Hls.js`.

### Step 3: Natural Language Neural Vector Search
1. In the search box at the top of the timeline, type any of the following queries:
   * `"highway traffic"` or `"moving cars"` &rarr; Filters instantly to CAM-01 highway events.
   * `"horses grazing"` or `"livestock pasture"` &rarr; Filters instantly to CAM-03 ranch events.
   * `"cashier checkout"` or `"retail counter queue"` &rarr; Filters instantly to CAM-04 store events.
   * `"pedestrians crossing"` or `"cyclist"` &rarr; Filters instantly to CAM-02 crosswalk events.
2. Click on any event card to trigger the **Video Review Modal**, showing the synchronized 5-second incident playback, primary label, confidence percentage, and timestamp.

---

## 4. Live Camera Testing Options

### Option A: Testing a Smartphone Camera (Takes 60 Seconds)
To demonstrate 100% genuine real-time video without dedicated CCTV cameras:
1. On an Android phone: Install **IP Webcam** (free on Google Play).
2. On an iPhone: Install **Live-Reporter** or **Live-Streamer**.
3. In the app, tap **Start Server**. Note the IP address shown on screen (e.g. `http://192.168.1.45:8080/video`).
4. On the Aiota Console, click **`[Test Stream URL]`** on CAM-01.
5. Paste the phone's video feed URL and click **Apply Live Feed**.
6. The phone's camera feed will stream directly inside the console tile with real-time motion.

### Option B: Testing External HLS Streams
1. Click **`[Test Stream URL]`** on any camera tile.
2. Paste any public HLS stream URL (`.m3u8`), such as:
   * Akamai Test Stream: `https://cph-p2p-msl.akamaized.net/hls/live/2000341/test/master.m3u8`
   * Unified Streaming: `https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8`
3. Click **Apply Live Feed** to render the stream live via `Hls.js`.
