# Marketing Landing Page for Aiota (Video Intelligence for Kenya & East Africa)

MARKETING_HTML = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth bg-slate-950 text-slate-100 antialiased">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aiota | Edge Video Intelligence Platform for Africa</title>
  <meta name="description" content="AI video intelligence built for Kenya. Works on your existing security cameras over Safaricom 4G. Natural language search, WhatsApp incident dispatch, and edge-first inference for farms, logistics, and construction.">
  <link rel="icon" type="image/svg+xml" href="/favicon.ico">
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    .glow-radial {
      background: radial-gradient(circle at 50% 0%, rgba(14, 165, 233, 0.15) 0%, rgba(15, 23, 42, 0) 70%);
    }
    .glow-card:hover {
      box-shadow: 0 0 35px -5px rgba(56, 189, 248, 0.2);
    }
  </style>
</head>
<body class="bg-[#070b14] text-slate-200 selection:bg-sky-500 selection:text-white">

  <!-- TOP NAVBAR -->
  <header class="sticky top-0 z-50 backdrop-blur-md bg-slate-950/80 border-b border-slate-800/80">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <a href="/" class="flex items-center space-x-2.5">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-600 to-cyan-400 text-white flex items-center justify-center font-black text-lg shadow-lg shadow-sky-500/20">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </div>
          <span class="font-black text-xl tracking-wider text-white">AIOTA</span>
          <span class="text-[10px] font-bold tracking-wider text-sky-400 bg-sky-950/80 border border-sky-800/60 px-2 py-0.5 rounded uppercase">Kenya</span>
        </a>
      </div>

      <!-- Desktop Navigation Links -->
      <nav class="hidden md:flex items-center space-x-8 text-sm font-medium text-slate-300">
        <a href="#features" class="hover:text-sky-400 transition">Capabilities</a>
        <a href="#verticals" class="hover:text-sky-400 transition">Verticals</a>
        <a href="#bandwidth" class="hover:text-sky-400 transition">4G Bandwidth</a>
        <a href="#hardware" class="hover:text-sky-400 transition">Aiota Box</a>
        <a href="#pricing" class="hover:text-sky-400 transition">Pricing (KES)</a>
      </nav>

      <!-- CTA Buttons -->
      <div class="flex items-center space-x-3">
        {AUTH_NAV_BUTTONS}
        <button onclick="openLeadModal('Header CTA')" class="hidden sm:inline-flex items-center space-x-2 bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs transition shadow-lg shadow-sky-500/25">
          <span>Request 14-Day Pilot</span>
          <i class="fa-solid fa-arrow-right text-[10px]"></i>
        </button>
      </div>
    </div>
  </header>

  <!-- HERO SECTION -->
  <section class="relative pt-20 pb-16 overflow-hidden glow-radial">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
      
      <!-- Market Announcement Pill -->
      <div class="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-slate-900 border border-sky-500/30 text-xs text-sky-400 font-semibold mb-8 shadow-inner">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>The Spot AI Alternative Built for Sub-Saharan Africa</span>
        <span class="text-slate-600">|</span>
        <span class="text-slate-300">Safaricom 4G & Solar Ready</span>
      </div>

      <h1 class="text-4xl sm:text-6xl lg:text-7xl font-extrabold text-white tracking-tight leading-[1.1] max-w-5xl mx-auto">
        Turn Your Existing Cameras into <br class="hidden sm:inline" />
        <span class="bg-gradient-to-r from-sky-400 via-cyan-300 to-teal-400 bg-clip-text text-transparent">
          Autonomous AI Scouts
        </span>
      </h1>

      <p class="mt-6 text-base sm:text-lg text-slate-400 max-w-3xl mx-auto leading-relaxed">
        No expensive cloud streaming. No camera rip-and-replace. Aiota connects to your existing Hikvision, Dahua, or Axis cameras, runs real-time computer vision locally on an on-premise appliance, and dispatches verified incident cards straight to your phone via WhatsApp.
      </p>

      <!-- Action Buttons -->
      <div class="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
        <button onclick="openLeadModal('Hero CTA')" class="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-400 text-slate-950 font-extrabold text-sm hover:opacity-95 transition shadow-xl shadow-sky-500/25 flex items-center justify-center space-x-2">
          <i class="fa-solid fa-bolt"></i>
          <span>Deploy a 14-Day Trial on Your Site</span>
        </button>
        <a href="#interactive-demo" class="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 font-bold text-sm transition flex items-center justify-center space-x-2">
          <i class="fa-solid fa-play text-sky-400 text-xs"></i>
          <span>Experience Live Demo</span>
        </a>
      </div>

      <!-- Trust & Key Metrics Bar -->
      <div class="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto text-left">
        <div class="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4">
          <div class="text-2xl sm:text-3xl font-extrabold text-white font-mono">99.4%</div>
          <div class="text-xs text-slate-400 mt-1">Bandwidth Savings vs Cloud VMS</div>
        </div>
        <div class="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4">
          <div class="text-2xl sm:text-3xl font-extrabold text-sky-400 font-mono">&lt; 400ms</div>
          <div class="text-xs text-slate-400 mt-1">Natural Language Vector Search</div>
        </div>
        <div class="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4">
          <div class="text-2xl sm:text-3xl font-extrabold text-emerald-400 font-mono">0 KES</div>
          <div class="text-xs text-slate-400 mt-1">Camera Upgrade Cost (ONVIF)</div>
        </div>
        <div class="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4">
          <div class="text-2xl sm:text-3xl font-extrabold text-amber-400 font-mono">&lt; 5s</div>
          <div class="text-xs text-slate-400 mt-1">Instant WhatsApp Incident Delivery</div>
        </div>
      </div>
    </div>
  </section>

  <!-- INTERACTIVE DEMO TEASER SECTION -->
  <section id="interactive-demo" class="py-16 bg-slate-950 border-y border-slate-800/80">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-3xl mx-auto mb-10">
        <span class="text-xs uppercase tracking-widest text-sky-400 font-bold">Interactive Platform Preview</span>
        <h2 class="text-2xl sm:text-4xl font-extrabold text-white mt-2">Search 10,000 Hours of Footage in Seconds</h2>
        <p class="text-slate-400 text-sm mt-3">Instead of scrubbing timelines for hours, describe what happened in plain English. Powered by OpenCLIP embeddings & Qdrant Cloud vector search.</p>
      </div>

      <div class="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        <!-- Interactive Mock Search Bar -->
        <div class="p-4 sm:p-6 border-b border-slate-800 bg-slate-950/80 flex flex-col md:flex-row items-center justify-between gap-4">
          <div class="relative w-full md:max-w-2xl">
            <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-3 text-sky-400 text-sm"></i>
            <input type="text" id="demoQueryInput" readonly value="White pickup truck entering gate after hours" class="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-24 py-2.5 text-xs text-slate-100 font-mono focus:outline-none">
            <span class="absolute right-2.5 top-2 bg-sky-950 text-sky-300 border border-sky-800 text-[10px] font-bold px-2 py-0.5 rounded">
              Neural Vector
            </span>
          </div>

          <!-- Sample Query Chips -->
          <div class="flex items-center space-x-2 overflow-x-auto w-full md:w-auto text-xs pb-1 md:pb-0">
            <span class="text-slate-500 text-[11px] font-semibold shrink-0">Try Query:</span>
            <button onclick="setDemoQuery('White pickup truck entering gate after hours', '/media/gate_security.mp4', 'CAM-01: Main Security Gate', 'Vehicle Ingress Detected (Confidence 96%)', '0.96 match')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-sky-300 border border-slate-700 text-[11px] shrink-0 transition">
              🚗 Vehicle Ingress
            </button>
            <button onclick="setDemoQuery('Pedestrian walking along commercial perimeter', '/media/pedestrian_walkway.mp4', 'CAM-02: Commercial Walkway', 'Perimeter Foot Patrol Detected (Confidence 93%)', '0.93 match')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[11px] shrink-0 transition">
              🚶 Perimeter Turnstile
            </button>
            <button onclick="setDemoQuery('Worker near greenhouse packhouse perimeter', '/media/greenhouse_access.mp4', 'CAM-03: Greenhouse Packhouse', 'Restricted Area Ingress (Confidence 91%)', '0.91 match')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[11px] shrink-0 transition">
              🌺 Packhouse Breach
            </button>
          </div>
        </div>

        <!-- Video Player & Incident Metadata Preview -->
        <div class="grid grid-cols-1 lg:grid-cols-3">
          <div class="lg:col-span-2 bg-black relative aspect-video flex items-center justify-center">
            <video id="demoVideoPlayer" src="/media/gate_security.mp4" autoplay loop muted playsinline class="w-full h-full object-cover"></video>
            
            <div class="absolute top-3 left-3 bg-slate-950/80 backdrop-blur border border-slate-800 text-xs px-3 py-1.5 rounded-lg flex items-center space-x-2">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              <span id="demoCamLabel" class="text-white font-semibold">CAM-01: Main Security Gate</span>
            </div>

            <div class="absolute bottom-3 left-3 bg-red-950/90 border border-red-800/80 text-red-200 text-xs px-3 py-1.5 rounded-lg flex items-center space-x-2">
              <i class="fa-solid fa-triangle-exclamation text-red-400"></i>
              <span id="demoIncidentLabel">Vehicle Ingress Detected (Confidence 96%)</span>
            </div>

            <div class="absolute top-3 right-3 bg-sky-950/80 border border-sky-800/80 text-sky-300 font-mono text-[11px] px-2.5 py-1 rounded-lg">
              <span id="demoScoreLabel">0.96 match</span>
            </div>
          </div>

          <!-- Incident Dispatch Card (WhatsApp Mock) -->
          <div class="p-6 bg-slate-900 flex flex-col justify-between border-t lg:border-t-0 lg:border-l border-slate-800">
            <div>
              <div class="flex items-center space-x-2 text-xs font-bold text-emerald-400 mb-4">
                <i class="fa-brands fa-whatsapp text-lg"></i>
                <span>Instant WhatsApp Dispatch Card</span>
              </div>

              <!-- Message Bubble -->
              <div class="bg-emerald-950/30 border border-emerald-800/50 rounded-2xl p-4 text-xs text-slate-300 space-y-2">
                <div class="font-bold text-white flex items-center justify-between">
                  <span>🚨 AIOTA VERIFIED INCIDENT</span>
                  <span class="text-[10px] text-slate-500 font-mono">19:42 EAT</span>
                </div>
                <p><strong>Site:</strong> Naivasha Flower Ranch (Rift Valley)</p>
                <p><strong>Camera:</strong> North Gate Weighbridge</p>
                <p><strong>Detected:</strong> Vehicle entry outside scheduled window</p>
                <p><strong>Neural Confidence:</strong> 96% verified</p>
                <div class="pt-2 border-t border-emerald-900/50 flex items-center justify-between text-[11px]">
                  <span class="text-sky-400">View Snapshot & Video Clip &rarr;</span>
                  <span class="text-emerald-400 font-bold">Dispatch Acknowledged</span>
                </div>
              </div>

              <div class="mt-6 space-y-2 text-xs text-slate-400">
                <div class="flex items-center space-x-2">
                  <i class="fa-solid fa-check text-emerald-400"></i>
                  <span>Zero false alarms from insects, rain, or tree shadows</span>
                </div>
                <div class="flex items-center space-x-2">
                  <i class="fa-solid fa-check text-emerald-400"></i>
                  <span>No need to install separate mobile apps for guards</span>
                </div>
                <div class="flex items-center space-x-2">
                  <i class="fa-solid fa-check text-emerald-400"></i>
                  <span>Runs over basic Safaricom/Airtel WhatsApp bundles</span>
                </div>
              </div>
            </div>

            <div class="mt-6 pt-4 border-t border-slate-800">
              <a href="/login" class="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-xl flex items-center justify-center space-x-2 transition border border-slate-700">
                <i class="fa-solid fa-arrow-up-right-from-square text-sky-400"></i>
                <span>Launch Enterprise Console</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- CAPABILITIES / FEATURES GRID -->
  <section id="features" class="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center max-w-3xl mx-auto mb-16">
      <span class="text-xs uppercase tracking-widest text-sky-400 font-bold">Intelligent Video Infrastructure</span>
      <h2 class="text-3xl sm:text-5xl font-black text-white mt-2">Engineered for Remote African Realities</h2>
      <p class="text-slate-400 text-base mt-4">Western cloud cameras assume unlimited gigabit fiber. Aiota is engineered from the ground up for intermittent cellular connectivity, solar power fluctuations, and harsh environments.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <!-- Card 1 -->
      <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 transition glow-card flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center text-xl mb-5">
            <i class="fa-solid fa-brain"></i>
          </div>
          <h3 class="text-lg font-bold text-white mb-2">Natural Language Neural Search</h3>
          <p class="text-xs text-slate-400 leading-relaxed">
            Query your visual archive using plain language. OpenCLIP models embed video semantics directly into Qdrant Cloud, letting security teams locate any incident in sub-second queries.
          </p>
        </div>
        <div class="mt-6 pt-4 border-t border-slate-800/80 text-xs font-mono text-sky-400">
          // Qdrant Vector Engine
        </div>
      </div>

      <!-- Card 2 -->
      <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 transition glow-card flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center text-xl mb-5">
            <i class="fa-brands fa-whatsapp"></i>
          </div>
          <h3 class="text-lg font-bold text-white mb-2">WhatsApp Incident Dispatcher</h3>
          <p class="text-xs text-slate-400 leading-relaxed">
            Eliminates security guard fatigue. When a tripwire is breached after hours, farm managers and dispatch controllers receive an instant WhatsApp alert card with high-resolution snapshot proof.
          </p>
        </div>
        <div class="mt-6 pt-4 border-t border-slate-800/80 text-xs font-mono text-emerald-400">
          // Twilio & Meta Cloud API
        </div>
      </div>

      <!-- Card 3 -->
      <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 transition glow-card flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center text-xl mb-5">
            <i class="fa-solid fa-tower-broadcast"></i>
          </div>
          <h3 class="text-lg font-bold text-white mb-2">Cellular Traffic Shaper</h3>
          <p class="text-xs text-slate-400 leading-relaxed">
            Video never leaves your premises unless an incident occurs. Only lightweight 512-dimension vector metadata syncs over 4G, keeping data usage under 1GB/month even with 32 cameras.
          </p>
        </div>
        <div class="mt-6 pt-4 border-t border-slate-800/80 text-xs font-mono text-amber-400">
          // 99.4% Bandwidth Savings
        </div>
      </div>

      <!-- Card 4 -->
      <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 transition glow-card flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center text-xl mb-5">
            <i class="fa-solid fa-camera-rotate"></i>
          </div>
          <h3 class="text-lg font-bold text-white mb-2">Universal ONVIF Compatibility</h3>
          <p class="text-xs text-slate-400 leading-relaxed">
            Keep your existing cameras. Aiota seamlessly connects to Hikvision, Dahua, Uniview, Axis, Hanwha, or generic RTSP streams. No proprietary cameras, no locked contracts.
          </p>
        </div>
        <div class="mt-6 pt-4 border-t border-slate-800/80 text-xs font-mono text-purple-400">
          // Plug-and-Play Discovery
        </div>
      </div>

      <!-- Card 5 -->
      <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 transition glow-card flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center text-xl mb-5">
            <i class="fa-solid fa-shield-cat"></i>
          </div>
          <h3 class="text-lg font-bold text-white mb-2">Rural Predator & Rustling Protection</h3>
          <p class="text-xs text-slate-400 leading-relaxed">
            Distinguish between livestock, security guards, stray hyenas/coyotes, and armed intruders along vast perimeter fences where physical patrols cannot be everywhere at once.
          </p>
        </div>
        <div class="mt-6 pt-4 border-t border-slate-800/80 text-xs font-mono text-rose-400">
          // Tailored Animal Models
        </div>
      </div>

      <!-- Card 6 -->
      <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 transition glow-card flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400 flex items-center justify-center text-xl mb-5">
            <i class="fa-solid fa-coins"></i>
          </div>
          <h3 class="text-lg font-bold text-white mb-2">Kenyan M-Pesa Subscription Billing</h3>
          <p class="text-xs text-slate-400 leading-relaxed">
            Pay seamlessly in KES via Safaricom M-Pesa Daraja STK Push or direct business till. Instant automated activation without requiring international dollar credit cards.
          </p>
        </div>
        <div class="mt-6 pt-4 border-t border-slate-800/80 text-xs font-mono text-teal-400">
          // Daraja 2.0 Integrated
        </div>
      </div>
    </div>
  </section>

  <!-- KENYAN VERTICAL SOLUTIONS -->
  <section id="verticals" class="py-20 bg-slate-950 border-t border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-3xl mx-auto mb-16">
        <span class="text-xs uppercase tracking-widest text-sky-400 font-bold">Targeted Industry Applications</span>
        <h2 class="text-3xl sm:text-5xl font-black text-white mt-2">Built for Kenya's High-Stakes Operations</h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- Agriculture -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 flex flex-col justify-between">
          <div>
            <div class="flex items-center space-x-3 mb-4">
              <span class="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-lg">🌾</span>
              <div>
                <h3 class="text-xl font-bold text-white">Flower Farms & Agricultural Ranches</h3>
                <span class="text-xs text-slate-400">Naivasha, Laikipia, Mount Kenya, Timau</span>
              </div>
            </div>
            <p class="text-xs text-slate-300 leading-relaxed mb-4">
              Remote greenhouses and open pastures suffer from night break-ins, flower packhouse pilferage, and livestock rustling. Aiota secures perimeter boundaries with virtual AI tripwires and wildlife detection.
            </p>
            <ul class="space-y-2 text-xs text-slate-400">
              <li><i class="fa-solid fa-circle-check text-emerald-400 mr-2"></i>Predator & livestock fence line tracking</li>
              <li><i class="fa-solid fa-circle-check text-emerald-400 mr-2"></i>Cold-room & packaging area access audits</li>
              <li><i class="fa-solid fa-circle-check text-emerald-400 mr-2"></i>Operates flawlessly over solar and battery backup</li>
            </ul>
          </div>
          <div class="mt-6 pt-4 border-t border-slate-800 flex justify-between items-center text-xs">
            <span class="text-slate-500">Typical Deployment: 12-32 Cameras</span>
            <button onclick="openLeadModal('Agriculture Vertical')" class="text-sky-400 font-bold hover:underline">Get Ranch Pilot &rarr;</button>
          </div>
        </div>

        <!-- Logistics -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 flex flex-col justify-between">
          <div>
            <div class="flex items-center space-x-3 mb-4">
              <span class="w-10 h-10 rounded-xl bg-sky-500/10 text-sky-400 flex items-center justify-center text-lg">🚚</span>
              <div>
                <h3 class="text-xl font-bold text-white">Logistics Yards & Inland Container Depots</h3>
                <span class="text-xs text-slate-400">Mombasa Road, Athi River, Embakasi ICD</span>
              </div>
            </div>
            <p class="text-xs text-slate-300 leading-relaxed mb-4">
              Track freight trucks entering and exiting your facility. Log turnaround dwell time, prevent loading dock bottlenecks, and alert safety officers when pedestrians walk into forklift blind spots.
            </p>
            <ul class="space-y-2 text-xs text-slate-400">
              <li><i class="fa-solid fa-circle-check text-sky-400 mr-2"></i>Truck weighbridge and gate turn-around logging</li>
              <li><i class="fa-solid fa-circle-check text-sky-400 mr-2"></i>Forklift & worker collision risk warnings</li>
              <li><i class="fa-solid fa-circle-check text-sky-400 mr-2"></i>Automated cargo security video seals</li>
            </ul>
          </div>
          <div class="mt-6 pt-4 border-t border-slate-800 flex justify-between items-center text-xs">
            <span class="text-slate-500">Typical Deployment: 20-64 Cameras</span>
            <button onclick="openLeadModal('Logistics Vertical')" class="text-sky-400 font-bold hover:underline">Get Depot Pilot &rarr;</button>
          </div>
        </div>

        <!-- Construction -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 flex flex-col justify-between">
          <div>
            <div class="flex items-center space-x-3 mb-4">
              <span class="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center text-lg">🏗️</span>
              <div>
                <h3 class="text-xl font-bold text-white">Construction & Infrastructure Sites</h3>
                <span class="text-xs text-slate-400">Westlands, Upper Hill, Kilimani, Tatu City</span>
              </div>
            </div>
            <p class="text-xs text-slate-300 leading-relaxed mb-4">
              Construction sites face constant diesel fuel siphoning, copper wire theft, and dangerous OSHA/PPE non-compliance. Aiota monitors high-value material yards 24/7 without requiring guards to stare at monitors.
            </p>
            <ul class="space-y-2 text-xs text-slate-400">
              <li><i class="fa-solid fa-circle-check text-amber-400 mr-2"></i>Real-time helmet and safety vest detection</li>
              <li><i class="fa-solid fa-circle-check text-amber-400 mr-2"></i>Machinery and fuel depot after-hours tripwires</li>
              <li><i class="fa-solid fa-circle-check text-amber-400 mr-2"></i>Subcontractor entry timestamp ledger</li>
            </ul>
          </div>
          <div class="mt-6 pt-4 border-t border-slate-800 flex justify-between items-center text-xs">
            <span class="text-slate-500">Typical Deployment: 8-24 Cameras</span>
            <button onclick="openLeadModal('Construction Vertical')" class="text-sky-400 font-bold hover:underline">Get Site Pilot &rarr;</button>
          </div>
        </div>

        <!-- Retail & Commercial -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 flex flex-col justify-between">
          <div>
            <div class="flex items-center space-x-3 mb-4">
              <span class="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center text-lg">🛍️</span>
              <div>
                <h3 class="text-xl font-bold text-white">Commercial Properties & Retail Hubs</h3>
                <span class="text-xs text-slate-400">Nairobi CBD, Karen, Sarit Centre, Nyali</span>
              </div>
            </div>
            <p class="text-xs text-slate-300 leading-relaxed mb-4">
              Unlock actionable intelligence from customer foot traffic. Discover peak shopping hours, queue dwell times, and perimeter loitering across shopping malls, petrol station forecourts, and retail chains.
            </p>
            <ul class="space-y-2 text-xs text-slate-400">
              <li><i class="fa-solid fa-circle-check text-purple-400 mr-2"></i>Footfall counts & customer dwell heatmaps</li>
              <li><i class="fa-solid fa-circle-check text-purple-400 mr-2"></i>Cash counter & till monitoring</li>
              <li><i class="fa-solid fa-circle-check text-purple-400 mr-2"></i>VIP vs suspicious loitering detection</li>
            </ul>
          </div>
          <div class="mt-6 pt-4 border-t border-slate-800 flex justify-between items-center text-xs">
            <span class="text-slate-500">Typical Deployment: 16-48 Cameras</span>
            <button onclick="openLeadModal('Retail Vertical')" class="text-sky-400 font-bold hover:underline">Get Retail Pilot &rarr;</button>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- BANDWIDTH COMPARISON -->
  <section id="bandwidth" class="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 rounded-3xl p-8 sm:p-12">
      <div class="max-w-3xl mx-auto text-center mb-12">
        <span class="text-xs uppercase tracking-widest text-sky-400 font-bold">The Bandwidth Breakthrough</span>
        <h2 class="text-3xl sm:text-4xl font-extrabold text-white mt-2">Why Cloud Cameras Fail in Kenya</h2>
        <p class="text-slate-400 text-sm mt-3">Legacy cloud systems upload continuous video streams 24/7. Over 4G cellular links, this destroys your monthly operating budget and causes constant stream drops.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- Legacy Cloud VMS -->
        <div class="bg-red-950/20 border border-red-900/40 rounded-2xl p-6">
          <div class="flex items-center space-x-2 text-red-400 font-bold text-sm mb-4">
            <i class="fa-solid fa-xmark"></i>
            <span>Standard Cloud Cameras (Verkada / Nest / Eagle Eye)</span>
          </div>
          <div class="space-y-4 text-xs text-slate-300">
            <div class="flex justify-between border-b border-red-900/30 pb-2">
              <span class="text-slate-400">Monthly Data per Camera:</span>
              <span class="font-bold font-mono text-red-400">180 GB / camera</span>
            </div>
            <div class="flex justify-between border-b border-red-900/30 pb-2">
              <span class="text-slate-400">16-Camera 4G Data Bill:</span>
              <span class="font-bold font-mono text-red-400">KES 85,000+ / mo</span>
            </div>
            <div class="flex justify-between border-b border-red-900/30 pb-2">
              <span class="text-slate-400">When 4G Drops:</span>
              <span class="text-red-400 font-bold">Zero recording. Blind spots.</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Hardware Requirement:</span>
              <span class="text-slate-400">Proprietary expensive cameras</span>
            </div>
          </div>
        </div>

        <!-- Aiota Edge Solution -->
        <div class="bg-sky-950/20 border border-sky-800/40 rounded-2xl p-6">
          <div class="flex items-center space-x-2 text-sky-400 font-bold text-sm mb-4">
            <i class="fa-solid fa-check"></i>
            <span>Aiota Edge-First Architecture</span>
          </div>
          <div class="space-y-4 text-xs text-slate-300">
            <div class="flex justify-between border-b border-sky-900/30 pb-2">
              <span class="text-slate-400">Monthly Data per Camera:</span>
              <span class="font-bold font-mono text-emerald-400">&lt; 0.8 GB / camera</span>
            </div>
            <div class="flex justify-between border-b border-sky-900/30 pb-2">
              <span class="text-slate-400">16-Camera 4G Data Bill:</span>
              <span class="font-bold font-mono text-emerald-400">&lt; KES 2,500 / mo</span>
            </div>
            <div class="flex justify-between border-b border-sky-900/30 pb-2">
              <span class="text-slate-400">When 4G Drops:</span>
              <span class="text-emerald-400 font-bold">Records continuously on local NVMe.</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Hardware Requirement:</span>
              <span class="text-sky-300 font-bold">Your existing IP cameras (any brand)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- HARDWARE APPLIANCE: AIOTA BOX -->
  <section id="hardware" class="py-20 bg-slate-950 border-t border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <div>
          <span class="text-xs uppercase tracking-widest text-sky-400 font-bold">On-Premise Appliance</span>
          <h2 class="text-3xl sm:text-5xl font-black text-white mt-2 leading-tight">The Aiota Box: Silent AI Workhorse</h2>
          <p class="text-slate-400 text-sm mt-4 leading-relaxed">
            A ruggedized, fanless edge computer deployed directly on your local network. It runs real-time YOLOv8 neural inference, maintains continuous 30-day NVMe local storage, and communicates securely with the Aiota Cloud Hub over Safaricom/Airtel 4G.
          </p>

          <div class="mt-8 space-y-3 text-xs">
            <div class="flex items-center space-x-3 bg-slate-900 border border-slate-800 p-3 rounded-xl">
              <i class="fa-solid fa-microchip text-sky-400 text-base"></i>
              <div>
                <span class="font-bold text-white">Intel 12th Gen N100 / Coral Dual TPU</span>
                <p class="text-slate-400 text-[11px]">Real-time concurrent object detection across up to 32 video streams.</p>
              </div>
            </div>

            <div class="flex items-center space-x-3 bg-slate-900 border border-slate-800 p-3 rounded-xl">
              <i class="fa-solid fa-hard-drive text-emerald-400 text-base"></i>
              <div>
                <span class="font-bold text-white">1TB - 4TB High-Endurance NVMe Storage</span>
                <p class="text-slate-400 text-[11px]">30 to 90 days continuous local loop recording. Zero cloud storage fees.</p>
              </div>
            </div>

            <div class="flex items-center space-x-3 bg-slate-900 border border-slate-800 p-3 rounded-xl">
              <i class="fa-solid fa-plug-circle-bolt text-amber-400 text-base"></i>
              <div>
                <span class="font-bold text-white">15W Low-Power Solar Inverter Compatible</span>
                <p class="text-slate-400 text-[11px]">Fanless, sealed aluminum chassis resistant to dust, humidity, and heat.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Appliance Graphic Box -->
        <div class="bg-gradient-to-tr from-slate-900 via-slate-900 to-sky-950/40 border border-slate-800 rounded-3xl p-8 relative flex flex-col items-center text-center">
          <div class="w-24 h-24 rounded-2xl bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center text-4xl mb-6 shadow-xl shadow-sky-500/10">
            <i class="fa-solid fa-server"></i>
          </div>
          <span class="font-mono text-xs uppercase tracking-widest text-sky-400 font-bold">Appliance Model N-100</span>
          <h3 class="text-2xl font-black text-white mt-1">Aiota Edge Box v2</h3>
          <p class="text-slate-400 text-xs mt-2 max-w-sm">Plugged into your local PoE switch. Automatically discovers cameras on your network in under 90 seconds.</p>

          <div class="mt-6 flex items-center space-x-2 text-[11px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-3 py-1.5 rounded-full">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
            <span>ONVIF Auto-Discovery Ready</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- TRANSPARENT PRICING IN KES -->
  <section id="pricing" class="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center max-w-3xl mx-auto mb-16">
      <span class="text-xs uppercase tracking-widest text-sky-400 font-bold">Transparent Subscription Billing</span>
      <h2 class="text-3xl sm:text-5xl font-black text-white mt-2">Priced for Sustainable ROI in Kenya</h2>
      <p class="text-slate-400 text-sm mt-3">No hidden cloud egress fees. Pay via M-Pesa STK Push or monthly corporate invoice.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Tier 1: Starter -->
      <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
        <div>
          <span class="text-xs uppercase font-bold text-slate-400">Farm / Small Site</span>
          <h3 class="text-xl font-bold text-white mt-1">Starter Tier</h3>
          <div class="mt-4 flex items-baseline text-white">
            <span class="text-3xl font-extrabold font-mono">KES 18,000</span>
            <span class="text-slate-400 text-xs ml-1">/ month</span>
          </div>
          <p class="text-slate-400 text-xs mt-2">Ideal for retail shops, fuel stations, and small flower farm gates.</p>

          <ul class="mt-6 space-y-2.5 text-xs text-slate-300">
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>Up to 4 Cameras</li>
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>Virtual AI Tripwires</li>
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>WhatsApp Incident Cards (1 Manager)</li>
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>14-Day Local Video Buffer</li>
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>M-Pesa STK Push Billing</li>
          </ul>
        </div>
        <button onclick="openLeadModal('Starter Tier (KES 18,000)')" class="mt-8 w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-xl border border-slate-700 transition">
          Choose Starter
        </button>
      </div>

      <!-- Tier 2: Enterprise (Highlighted) -->
      <div class="bg-gradient-to-b from-slate-900 to-sky-950/40 border-2 border-sky-500 rounded-2xl p-6 relative flex flex-col justify-between shadow-2xl shadow-sky-500/10">
        <span class="absolute -top-3 left-1/2 -translate-x-1/2 bg-sky-500 text-slate-950 text-[10px] uppercase font-black px-3 py-0.5 rounded-full">
          Most Popular in Kenya
        </span>
        <div>
          <span class="text-xs uppercase font-bold text-sky-400">Depots & Large Farms</span>
          <h3 class="text-xl font-bold text-white mt-1">Enterprise Tier</h3>
          <div class="mt-4 flex items-baseline text-white">
            <span class="text-3xl font-extrabold font-mono text-sky-400">KES 48,000</span>
            <span class="text-slate-400 text-xs ml-1">/ month</span>
          </div>
          <p class="text-slate-400 text-xs mt-2">Comprehensive visual intelligence across multi-camera facilities.</p>

          <ul class="mt-6 space-y-2.5 text-xs text-slate-200">
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>Up to 16 Cameras</li>
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i><strong>Aiota Box N100 Hardware Included</strong></li>
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>Sub-Second Natural Language Search</li>
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>Multi-Recipient WhatsApp Incident Routing</li>
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>30-Day High-Endurance Storage</li>
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>Dedicated On-Site Technician Setup</li>
          </ul>
        </div>
        <button onclick="openLeadModal('Enterprise Tier (KES 48,000)')" class="mt-8 w-full py-3 bg-sky-500 hover:bg-sky-400 text-slate-950 font-extrabold text-xs rounded-xl shadow-lg shadow-sky-500/25 transition">
          Start 14-Day Enterprise Trial
        </button>
      </div>

      <!-- Tier 3: Industrial / Multi-Site -->
      <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
        <div>
          <span class="text-xs uppercase font-bold text-slate-400">Multi-Site Operations</span>
          <h3 class="text-xl font-bold text-white mt-1">Industrial / Estate</h3>
          <div class="mt-4 flex items-baseline text-white">
            <span class="text-3xl font-extrabold font-mono">Custom</span>
            <span class="text-slate-400 text-xs ml-1">KES / site</span>
          </div>
          <p class="text-slate-400 text-xs mt-2">For logistics conglomerates, tea estates, and nationwide retail networks.</p>

          <ul class="mt-6 space-y-2.5 text-xs text-slate-300">
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>16+ to 200+ Cameras</li>
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>Multi-Appliance Cluster Failover</li>
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>Custom Domain Fine-Tuning</li>
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>ERP & Weighbridge API Webhooks</li>
            <li><i class="fa-solid fa-check text-sky-400 mr-2"></i>SLA Guaranteed Replacement Appliance</li>
          </ul>
        </div>
        <button onclick="openLeadModal('Industrial / Custom Quote')" class="mt-8 w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-xl border border-slate-700 transition">
          Speak with Engineering
        </button>
      </div>
    </div>
  </section>

  <!-- FINAL CTA BANNER -->
  <section class="py-16 bg-gradient-to-r from-sky-950/40 via-slate-900 to-slate-950 border-t border-slate-800">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <h2 class="text-3xl sm:text-4xl font-extrabold text-white">Ready to Put Your Cameras on Autopilot?</h2>
      <p class="text-slate-400 text-sm mt-3 max-w-2xl mx-auto">
        Join leading Kenyan logistics operators and agricultural estates using Aiota. We dispatch an appliance to your site for a zero-risk 14-day evaluation.
      </p>

      <div class="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
        <button onclick="openLeadModal('Bottom Banner')" class="w-full sm:w-auto px-8 py-3.5 bg-sky-500 hover:bg-sky-400 text-slate-950 font-extrabold text-sm rounded-xl shadow-xl shadow-sky-500/20 transition">
          Schedule Your 14-Day On-Site Pilot
        </button>
        <a href="https://wa.me/254712345678?text=Hello%20Aiota%20team,%20I%20am%20interested%20in%20a%20video%20intelligence%20demo%20for%20my%20site." target="_blank" class="w-full sm:w-auto px-6 py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm rounded-xl transition flex items-center justify-center space-x-2">
          <i class="fa-brands fa-whatsapp text-lg"></i>
          <span>Chat on WhatsApp</span>
        </a>
      </div>
    </div>
  </section>

  <!-- FOOTER -->
  <footer class="border-t border-slate-900 bg-slate-950/90 py-12 text-xs text-slate-500">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center gap-6">
      <div class="flex items-center space-x-3">
        <div class="w-6 h-6 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold text-xs">
          A
        </div>
        <span class="text-slate-300 font-bold tracking-wider">AIOTA ENTERPRISE</span>
        <span class="text-slate-700">|</span>
        <span>Akilinova Technologies Ltd • Nairobi, Kenya</span>
      </div>

      <div class="flex items-center space-x-6">
        <a href="#features" class="hover:text-slate-300 transition">Features</a>
        <a href="#verticals" class="hover:text-slate-300 transition">Verticals</a>
        <a href="#pricing" class="hover:text-slate-300 transition">Pricing</a>
        <a href="/api/docs" class="hover:text-sky-400 transition">API Docs</a>
        <a href="/login" class="text-sky-400 hover:text-sky-300 font-bold transition">Console Sign In &rarr;</a>
      </div>
    </div>
  </footer>

  <!-- LEAD CAPTURE MODAL -->
  <div id="leadModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl relative">
      <button onclick="closeLeadModal()" class="absolute top-5 right-5 text-slate-400 hover:text-white transition">
        <i class="fa-solid fa-xmark text-lg"></i>
      </button>

      <div class="mb-5">
        <span class="text-[10px] uppercase font-bold tracking-widest text-sky-400">Zero-Risk Evaluation</span>
        <h3 class="text-xl font-bold text-white mt-1">Request a 14-Day On-Site Pilot</h3>
        <p class="text-xs text-slate-400 mt-1">We will configure an Aiota Box and connect it to your existing security cameras.</p>
      </div>

      <form id="leadForm" onsubmit="submitLead(event)" class="space-y-3.5 text-xs">
        <div>
          <label class="block text-slate-300 font-semibold mb-1">Company / Facility Name</label>
          <input type="text" id="leadCompany" required placeholder="e.g. Naivasha Bloom Farms / Mombasa Logistics Depot" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-100 focus:outline-none focus:border-sky-500">
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-slate-300 font-semibold mb-1">Contact Person</label>
            <input type="text" id="leadName" required placeholder="e.g. David Mwangi" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-100 focus:outline-none focus:border-sky-500">
          </div>
          <div>
            <label class="block text-slate-300 font-semibold mb-1">WhatsApp / Phone Number</label>
            <input type="text" id="leadPhone" required placeholder="+254 7..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-100 focus:outline-none focus:border-sky-500">
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-slate-300 font-semibold mb-1">Facility Location</label>
            <input type="text" id="leadLocation" placeholder="e.g. Naivasha / Nairobi ICD" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-100 focus:outline-none focus:border-sky-500">
          </div>
          <div>
            <label class="block text-slate-300 font-semibold mb-1">Approx. Number of Cameras</label>
            <select id="leadCameras" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-100 focus:outline-none focus:border-sky-500">
              <option value="1-4">1 - 4 Cameras</option>
              <option value="5-16" selected>5 - 16 Cameras</option>
              <option value="17-32">17 - 32 Cameras</option>
              <option value="32+">32+ Cameras</option>
            </select>
          </div>
        </div>

        <input type="hidden" id="leadSource" value="Landing Page">

        <div id="leadSuccess" class="hidden bg-emerald-950/80 border border-emerald-800 text-emerald-200 text-xs p-3 rounded-xl flex items-center space-x-2">
          <i class="fa-solid fa-circle-check text-emerald-400 text-base"></i>
          <span>Thank you! Our Nairobi engineering team has received your pilot request and will contact you via WhatsApp shortly.</span>
        </div>

        <button type="submit" id="leadSubmitBtn" class="w-full py-3 bg-sky-500 hover:bg-sky-400 text-slate-950 font-extrabold text-xs rounded-xl shadow-lg shadow-sky-500/20 transition flex items-center justify-center space-x-2">
          <span>Submit Pilot Request</span>
          <i class="fa-solid fa-arrow-right text-[10px]"></i>
        </button>
      </form>
    </div>
  </div>

  <script>
    function openLeadModal(source = 'Landing Page') {
      document.getElementById('leadSource').value = source;
      document.getElementById('leadModal').classList.remove('hidden');
    }

    function closeLeadModal() {
      document.getElementById('leadModal').classList.add('hidden');
    }

    function setDemoQuery(query, videoUrl, camLabel, incidentLabel, score) {
      document.getElementById('demoQueryInput').value = query;
      const v = document.getElementById('demoVideoPlayer');
      v.src = videoUrl;
      v.play();
      document.getElementById('demoCamLabel').innerText = camLabel;
      document.getElementById('demoIncidentLabel').innerText = incidentLabel;
      document.getElementById('demoScoreLabel').innerText = score;
    }

    async function submitLead(e) {
      e.preventDefault();
      const btn = document.getElementById('leadSubmitBtn');
      btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i><span>Submitting Request...</span>';
      btn.disabled = true;

      const payload = {
        company: document.getElementById('leadCompany').value,
        name: document.getElementById('leadName').value,
        phone: document.getElementById('leadPhone').value,
        location: document.getElementById('leadLocation').value,
        cameras: document.getElementById('leadCameras').value,
        source: document.getElementById('leadSource').value
      };

      try {
        await fetch('/api/lead-capture', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
      } catch (err) {
        console.warn('Network log:', err);
      }

      document.getElementById('leadSuccess').classList.remove('hidden');
      btn.classList.add('hidden');
      setTimeout(() => {
        closeLeadModal();
        document.getElementById('leadSuccess').classList.add('hidden');
        btn.classList.remove('hidden');
        btn.innerHTML = '<span>Submit Pilot Request</span><i class="fa-solid fa-arrow-right text-[10px]"></i>';
        btn.disabled = false;
      }, 4000);
    }
  </script>
</body>
</html>"""
