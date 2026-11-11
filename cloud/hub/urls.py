import json
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from app.api.endpoints import api
from app.core.models import Organization, OrganizationMember, Camera, DetectionEvent

try:
    from app.marketing import MARKETING_HTML
except ImportError:
    try:
        from cloud.hub.marketing import MARKETING_HTML
    except ImportError:
        from marketing import MARKETING_HTML

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#0284c7"/>
    </linearGradient>
  </defs>
  <rect width="32" height="32" rx="8" fill="#0b1329"/>
  <rect x="1" y="1" width="30" height="30" rx="7" fill="none" stroke="#1e293b" stroke-width="1"/>
  <path d="M16 8C9 8 4 16 4 16s5 8 12 8 12-8 12-8-5-8-12-8z" fill="none" stroke="url(#g)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="16" cy="16" r="4.5" fill="#0284c7"/>
  <circle cx="16" cy="16" r="2" fill="#f8fafc"/>
  <circle cx="17.2" cy="14.8" r="1" fill="#ffffff"/>
</svg>"""

LOGIN_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class="h-full bg-slate-950">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aiota | Intelligent Video Surveillance</title>
  <link rel="icon" type="image/svg+xml" href="/favicon.ico">
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
  </style>
</head>
<body class="h-full bg-[#060a12] flex items-center justify-center p-4 sm:p-6 text-slate-100 antialiased relative overflow-hidden select-none">
  <!-- Subtle Ambient Glows -->
  <div class="absolute -top-40 -left-40 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl pointer-events-none"></div>
  <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>

  <div class="w-full max-w-[420px] relative z-10">
    <!-- Card Container -->
    <div class="bg-gradient-to-b from-slate-900/90 to-slate-950/90 border border-slate-800/80 rounded-2xl shadow-2xl backdrop-blur-xl overflow-hidden">
      
      <!-- Top Brand Header -->
      <div class="px-8 pt-8 pb-6 text-center border-b border-slate-800/60 bg-slate-950/40">
        <!-- Brand Logo Icon -->
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-sky-400/20 to-sky-600/10 border border-sky-400/30 text-sky-400 flex items-center justify-center mx-auto mb-3 shadow-lg shadow-sky-500/10">
          <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </div>

        <div class="flex items-center justify-center space-x-2">
          <span class="text-xl font-extrabold tracking-wider text-white">AIOTA</span>
          <span class="text-[10px] font-bold tracking-widest text-sky-400 bg-sky-950/80 border border-sky-800/60 px-2 py-0.5 rounded uppercase">Enterprise</span>
        </div>
        <p class="text-xs text-slate-400 mt-1.5 font-medium">Remote Video Intelligence & Security Platform</p>
      </div>

      <!-- Login Form -->
      <form method="POST" action="/login" class="p-8 space-y-4">
        <!-- Error Alert (shown on failure) -->
        {ERROR_MESSAGE_BLOCK}

        <!-- Username / Email Field -->
        <div>
          <label class="block text-[11px] font-bold uppercase tracking-wider text-slate-300 mb-1.5">Username or Email</label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
              <i class="fa-solid fa-user text-xs"></i>
            </span>
            <input type="text" name="username" required autocomplete="username" placeholder="admin" value="admin"
              class="w-full pl-10 pr-4 py-2.5 bg-slate-950/90 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-600 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition shadow-inner font-medium" />
          </div>
        </div>

        <!-- Password Field -->
        <div>
          <div class="flex justify-between items-center mb-1.5">
            <label class="block text-[11px] font-bold uppercase tracking-wider text-slate-300">Password</label>
            <span class="text-[10px] text-slate-500 font-medium">Case-sensitive</span>
          </div>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
              <i class="fa-solid fa-lock text-xs"></i>
            </span>
            <input type="password" id="passInput" name="password" required autocomplete="current-password" placeholder="••••••••" value="Admin@Akilinova2026!"
              class="w-full pl-10 pr-10 py-2.5 bg-slate-950/90 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-600 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition shadow-inner font-medium" />
            <button type="button" onclick="togglePassVisibility()" class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-500 hover:text-slate-300 transition">
              <i id="passIcon" class="fa-solid fa-eye-slash text-xs"></i>
            </button>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="pt-2">
          <button type="submit" class="w-full py-3 bg-gradient-to-r from-sky-600 to-sky-500 hover:from-sky-500 hover:to-sky-400 text-white text-xs font-bold uppercase tracking-wider rounded-xl transition shadow-lg shadow-sky-600/25 flex items-center justify-center space-x-2 active:scale-[0.99]">
            <span>Sign In to Dashboard</span>
            <i class="fa-solid fa-arrow-right text-xs"></i>
          </button>
        </div>

        <!-- Demo Credentials Pill (Clean & legible) -->
        <div class="mt-4 pt-4 border-t border-slate-800/80 bg-slate-950/60 rounded-xl p-3 border border-slate-800/50">
          <div class="flex items-center justify-between text-[11px] text-slate-400 mb-1">
            <span class="font-semibold text-slate-300 flex items-center">
              <i class="fa-solid fa-key mr-1.5 text-sky-400"></i>Preloaded Demo Account:
            </span>
            <span class="text-[10px] text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800/40 font-mono">OWNER</span>
          </div>
          <div class="grid grid-cols-2 gap-2 text-xs font-mono mt-1 text-slate-300 bg-slate-900/80 p-2 rounded-lg border border-slate-800">
            <div>
              <span class="text-[10px] text-slate-500 block">User:</span>
              <strong class="text-white select-all">admin</strong>
            </div>
            <div>
              <span class="text-[10px] text-slate-500 block">Pass:</span>
              <strong class="text-sky-300 select-all">Admin@Akilinova2026!</strong>
            </div>
          </div>
        </div>
      </form>
    </div>

    <!-- Footer Note -->
    <div class="mt-4 text-center">
      <p class="text-[11px] text-slate-500 flex items-center justify-center space-x-2">
        <span>Powered by Akilinova Vision</span>
        <span>•</span>
        <span class="flex items-center text-emerald-400">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-1"></span> Qdrant GCP Connected
        </span>
      </p>
    </div>
  </div>

  <script>
    function togglePassVisibility() {
      const p = document.getElementById('passInput');
      const icon = document.getElementById('passIcon');
      if (p.type === 'password') {
        p.type = 'text';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
      } else {
        p.type = 'password';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
      }
    }
  </script>
</body>
</html>"""

DASHBOARD_AUTH_HTML = """<!DOCTYPE html>
<html lang="en" class="h-full bg-slate-950">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aiota Enterprise | Video Intelligence Platform</title>
  <link rel="icon" type="image/svg+xml" href="/favicon.ico">
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #090d16; }
    ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
  </style>
</head>
<body class="h-full bg-[#0a0f1d] text-slate-100 font-sans flex flex-col overflow-hidden antialiased select-none">

  <!-- TOP HEADER -->
  <header class="h-14 border-b border-slate-800/80 bg-slate-900/95 backdrop-blur px-4 flex items-center justify-between z-30 shrink-0">
    <div class="flex items-center space-x-6">
      <div class="flex items-center space-x-2.5">
        <div class="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center font-black text-lg border border-sky-500/30">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </div>
        <span class="font-extrabold text-base tracking-wider text-white">AIOTA</span>
        <span class="text-[10px] font-semibold tracking-wider text-sky-400 bg-sky-950/80 border border-sky-800/60 px-2 py-0.5 rounded uppercase">Enterprise</span>
      </div>

      <div class="hidden sm:flex items-center space-x-2 bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs">
        <i class="fa-solid fa-building text-sky-400"></i>
        <span class="text-slate-300 font-bold">{ORG_NAME}</span>
        <span class="text-slate-600">|</span>
        <select id="siteSelect" class="bg-transparent text-slate-300 focus:outline-none cursor-pointer font-medium">
          <option value="all">Naivasha Flower Ranch (Rift Valley)</option>
          <option value="mombasa">Mombasa Road Depots (Nairobi)</option>
        </select>
      </div>
    </div>

    <div class="flex items-center space-x-4">
      <div class="hidden md:flex items-center space-x-2 bg-slate-950 border border-slate-800 px-3 py-1 rounded-lg text-xs">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span class="text-slate-400">Safaricom 4G Uplink:</span>
        <span class="text-emerald-400 font-bold">Online</span>
      </div>

      <div class="flex items-center space-x-3 text-xs">
        <span class="text-slate-300 font-semibold"><i class="fa-solid fa-user-shield mr-1 text-sky-400"></i>{USERNAME} ({ROLE})</span>
        <a href="/logout" class="text-red-400 hover:text-red-300 border border-red-900/60 bg-red-950/40 px-2 py-1 rounded font-medium transition">
          <i class="fa-solid fa-right-from-bracket mr-1"></i>Sign Out
        </a>
      </div>
    </div>
  </header>

  <div class="flex-1 flex overflow-hidden">
    <!-- LEFT SIDEBAR -->
    <aside class="w-16 md:w-56 border-r border-slate-800/80 bg-slate-900/60 flex flex-col justify-between p-2 md:p-3 shrink-0">
      <div class="space-y-1">
        <button onclick="setTab('search')" id="tabBtnSearch" class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sky-400 bg-sky-500/10 border border-sky-500/20 text-xs font-semibold transition">
          <i class="fa-solid fa-magnifying-glass text-sm"></i>
          <span class="hidden md:inline">Neural Search</span>
        </button>

        <button onclick="setTab('wall')" id="tabBtnWall" class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 text-xs font-semibold transition">
          <i class="fa-solid fa-table-cells text-sm"></i>
          <span class="hidden md:inline">Camera Wall (Live)</span>
        </button>

        <button onclick="setTab('alerts')" id="tabBtnAlerts" class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 text-xs font-semibold transition">
          <i class="fa-brands fa-whatsapp text-sm"></i>
          <span class="hidden md:inline">WhatsApp Alerts</span>
          <span class="hidden md:inline-block ml-auto text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800 px-1.5 py-0.2 rounded-full font-bold">2</span>
        </button>

        <button onclick="setTab('appliances')" id="tabBtnAppliances" class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 text-xs font-semibold transition">
          <i class="fa-solid fa-server text-sm"></i>
          <span class="hidden md:inline">Aiota Boxes</span>
        </button>
      </div>

      <div class="pt-3 border-t border-slate-800/80">
        <button onclick="triggerSimulatedDetection()" id="btnSimulate" class="w-full bg-slate-800 hover:bg-sky-600 text-slate-200 hover:text-white px-2 py-2 rounded-xl text-[11px] font-semibold transition flex items-center justify-center space-x-2 border border-slate-700/60">
          <i class="fa-solid fa-plus-circle text-sky-400"></i>
          <span class="hidden md:inline">Simulate Detection</span>
        </button>
      </div>
    </aside>

    <!-- MAIN VIEWPORT -->
    <main class="flex-1 flex flex-col overflow-hidden bg-[#070b14]">

      <!-- TAB 1: INCIDENT SEARCH -->
      <section id="viewSearch" class="flex-1 flex flex-col overflow-hidden">
        <div class="border-b border-slate-800/80 bg-slate-900/40 p-4 space-y-3 shrink-0">
          <form id="searchForm" class="flex gap-2.5">
            <div class="relative flex-1">
              <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-3 text-slate-500 text-sm"></i>
              <input type="text" id="searchQuery" 
                placeholder="Search by natural language (e.g. 'coyote predator', 'intruder person at gate', 'tractor in feedlot', 'stray dog')..." 
                class="w-full pl-10 pr-4 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 transition shadow-inner" />
            </div>
            <button type="submit" class="px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs rounded-xl transition flex items-center space-x-2 shadow-lg shadow-sky-600/20 shrink-0">
              <i class="fa-solid fa-bolt"></i>
              <span>Neural Search</span>
            </button>
          </form>

          <div class="flex items-center space-x-2 overflow-x-auto pb-1 text-xs">
            <span class="text-slate-500 font-medium shrink-0">Quick Queries:</span>
            <button onclick="quickSearch('highway traffic cars vehicle')" class="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-sky-300 border border-slate-700/60 shrink-0 transition">
              🚗 Highway Traffic (Mombasa Rd)
            </button>
            <button onclick="quickSearch('pedestrians crosswalk cyclist bicycle')" class="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-emerald-300 border border-slate-700/60 shrink-0 transition">
              🚶 Crosswalk & Cyclists
            </button>
            <button onclick="quickSearch('horses livestock farm animals pasture')" class="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-amber-300 border border-slate-700/60 shrink-0 transition">
              🐎 Livestock at Fence (Ranch)
            </button>
            <button onclick="quickSearch('retail store cashier till checkout queue')" class="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-purple-300 border border-slate-700/60 shrink-0 transition">
              🛍️ Retail Checkout & Till
            </button>
            <button onclick="quickSearch('vehicle parking lot parked cars')" class="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/60 shrink-0 transition">
              🅿️ Facility Parking Yard
            </button>
          </div>
        </div>

        <div class="h-9 border-b border-slate-800/60 bg-slate-950/60 px-4 flex items-center justify-between text-xs text-slate-400 shrink-0">
          <div class="flex items-center space-x-3">
            <span class="font-medium text-slate-300"><i class="fa-regular fa-clock mr-1 text-sky-400"></i>24-Hour Event Timeline:</span>
            <div class="flex items-center space-x-1 font-mono text-[10px]">
              <span class="w-2.5 h-2.5 bg-slate-800 rounded"></span><span>Idle</span>
              <span class="w-2.5 h-2.5 bg-sky-500/80 rounded ml-2"></span><span>Motion</span>
              <span class="w-2.5 h-2.5 bg-red-500 rounded ml-2"></span><span>Verified Alert</span>
            </div>
          </div>
          <div id="statCounter" class="font-semibold text-slate-300">Loading events...</div>
        </div>

        <div class="flex-1 overflow-y-auto p-4 md:p-6">
          <div id="resultsGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          </div>
        </div>
      </section>

      <!-- TAB 2: LIVE CAMERA WALL (DEMO LOOPS & PUBLIC STREAMS) -->
      <section id="viewWall" class="flex-1 flex flex-col overflow-hidden hidden p-4">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 mb-3 shrink-0">
          <div>
            <h2 class="text-base font-bold text-white flex items-center space-x-2">
              <i class="fa-solid fa-table-cells text-sky-400"></i>
              <span id="wallTitle">Naivasha Flower Ranch - Live Camera Wall</span>
            </h2>
            <p class="text-xs text-slate-400" id="wallSubtitle">Live video streaming over WebRTC / HLS local buffer</p>
          </div>

          <div class="flex items-center space-x-2">
            <!-- Preset Switcher -->
            <div class="bg-slate-900 border border-slate-800 p-1 rounded-xl flex items-center space-x-1 text-xs">
              <button onclick="switchWallPreset('demo')" id="btnPresetDemo" class="px-3 py-1 rounded-lg font-semibold bg-sky-500/20 text-sky-300 border border-sky-500/30 transition flex items-center space-x-1.5">
                <i class="fa-solid fa-shield-halved text-[11px]"></i>
                <span>Demo CCTV Loops</span>
              </button>
              <button onclick="switchWallPreset('public')" id="btnPresetPublic" class="px-3 py-1 rounded-lg font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition flex items-center space-x-1.5">
                <i class="fa-solid fa-globe text-[11px]"></i>
                <span>Public Live Streams</span>
              </button>
            </div>

            <!-- Custom Stream Config Button -->
            <button onclick="openCustomStreamModal()" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-semibold rounded-xl border border-slate-700 text-slate-200 transition flex items-center space-x-1.5">
              <i class="fa-solid fa-sliders text-sky-400"></i>
              <span>Test Stream URL</span>
            </button>

            <span class="text-xs text-emerald-400 bg-emerald-950/60 border border-emerald-800/50 px-2.5 py-1.5 rounded-xl flex items-center">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping mr-2"></span> 4 Streams Active
            </span>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1 overflow-y-auto" id="cameraWallGrid">
          <!-- Cam 1 -->
          <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
            <div class="p-2.5 bg-slate-950 border-b border-slate-800 flex justify-between items-center text-xs font-semibold">
              <span class="text-slate-200" id="camTitle0"><i class="fa-solid fa-camera mr-1 text-sky-400"></i>CAM-01: North Perimeter Main Gate</span>
              <div class="flex items-center space-x-2">
                <button onclick="openCustomStreamModal(0)" class="text-[11px] text-slate-400 hover:text-sky-400 transition" title="Change stream">
                  <i class="fa-solid fa-pen-to-square"></i>
                </button>
                <span class="text-[10px] text-emerald-400 font-mono" id="camRes0">1080p @ 15fps</span>
              </div>
            </div>
            <div class="flex-1 bg-black relative aspect-video flex items-center justify-center">
              <video id="camVideo0" autoplay loop muted playsinline class="w-full h-full object-cover"></video>
              <div class="absolute bottom-2 left-2 text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-mono font-bold flex items-center shadow-lg" id="camBadge0">
                <span class="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse mr-1.5"></span> LIVE FEED
              </div>
              <div class="absolute top-2 right-2 text-[10px] bg-slate-950/80 text-slate-300 px-2 py-0.5 rounded font-mono" id="camTag0">
                RTSP-MAIN-01
              </div>
            </div>
          </div>

          <!-- Cam 2 -->
          <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
            <div class="p-2.5 bg-slate-950 border-b border-slate-800 flex justify-between items-center text-xs font-semibold">
              <span class="text-slate-200" id="camTitle1"><i class="fa-solid fa-camera mr-1 text-sky-400"></i>CAM-02: Commercial Perimeter Walkway</span>
              <div class="flex items-center space-x-2">
                <button onclick="openCustomStreamModal(1)" class="text-[11px] text-slate-400 hover:text-sky-400 transition" title="Change stream">
                  <i class="fa-solid fa-pen-to-square"></i>
                </button>
                <span class="text-[10px] text-emerald-400 font-mono" id="camRes1">1080p @ 15fps</span>
              </div>
            </div>
            <div class="flex-1 bg-black relative aspect-video flex items-center justify-center">
              <video id="camVideo1" autoplay loop muted playsinline class="w-full h-full object-cover"></video>
              <div class="absolute bottom-2 left-2 text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-mono font-bold flex items-center shadow-lg" id="camBadge1">
                <span class="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse mr-1.5"></span> LIVE FEED
              </div>
              <div class="absolute top-2 right-2 text-[10px] bg-slate-950/80 text-slate-300 px-2 py-0.5 rounded font-mono" id="camTag1">
                RTSP-SUB-02
              </div>
            </div>
          </div>

          <!-- Cam 3 -->
          <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
            <div class="p-2.5 bg-slate-950 border-b border-slate-800 flex justify-between items-center text-xs font-semibold">
              <span class="text-slate-200" id="camTitle2"><i class="fa-solid fa-camera mr-1 text-sky-400"></i>CAM-03: Greenhouse Packhouse Access</span>
              <div class="flex items-center space-x-2">
                <button onclick="openCustomStreamModal(2)" class="text-[11px] text-slate-400 hover:text-sky-400 transition" title="Change stream">
                  <i class="fa-solid fa-pen-to-square"></i>
                </button>
                <span class="text-[10px] text-emerald-400 font-mono" id="camRes2">1080p @ 15fps</span>
              </div>
            </div>
            <div class="flex-1 bg-black relative aspect-video flex items-center justify-center">
              <video id="camVideo2" autoplay loop muted playsinline class="w-full h-full object-cover"></video>
              <div class="absolute bottom-2 left-2 text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-mono font-bold flex items-center shadow-lg" id="camBadge2">
                <span class="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse mr-1.5"></span> LIVE FEED
              </div>
              <div class="absolute top-2 right-2 text-[10px] bg-slate-950/80 text-slate-300 px-2 py-0.5 rounded font-mono" id="camTag2">
                RTSP-SUB-03
              </div>
            </div>
          </div>

          <!-- Cam 4 -->
          <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
            <div class="p-2.5 bg-slate-950 border-b border-slate-800 flex justify-between items-center text-xs font-semibold">
              <span class="text-slate-200" id="camTitle3"><i class="fa-solid fa-camera mr-1 text-sky-400"></i>CAM-04: Fuel Depot & Machinery Yard</span>
              <div class="flex items-center space-x-2">
                <button onclick="openCustomStreamModal(3)" class="text-[11px] text-slate-400 hover:text-sky-400 transition" title="Change stream">
                  <i class="fa-solid fa-pen-to-square"></i>
                </button>
                <span class="text-[10px] text-emerald-400 font-mono" id="camRes3">1080p @ 15fps</span>
              </div>
            </div>
            <div class="flex-1 bg-black relative aspect-video flex items-center justify-center">
              <video id="camVideo3" autoplay loop muted playsinline class="w-full h-full object-cover"></video>
              <div class="absolute bottom-2 left-2 text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-mono font-bold flex items-center shadow-lg" id="camBadge3">
                <span class="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse mr-1.5"></span> LIVE FEED
              </div>
              <div class="absolute top-2 right-2 text-[10px] bg-slate-950/80 text-slate-300 px-2 py-0.5 rounded font-mono" id="camTag3">
                RTSP-SUB-04
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- MODAL: CUSTOM STREAM TESTER -->
      <div id="streamModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
          <div class="flex justify-between items-center border-b border-slate-800 pb-3">
            <h3 class="text-base font-bold text-white flex items-center space-x-2">
              <i class="fa-solid fa-video text-sky-400"></i>
              <span>Connect / Test Live CCTV Stream</span>
            </h3>
            <button onclick="closeCustomStreamModal()" class="text-slate-400 hover:text-white transition">
              <i class="fa-solid fa-xmark text-lg"></i>
            </button>
          </div>

          <div class="space-y-3 text-xs">
            <div>
              <label class="block text-slate-300 font-semibold mb-1">Target Camera Slot</label>
              <select id="modalCamSelect" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-sky-500">
                <option value="0">CAM-01 (Tile 1)</option>
                <option value="1">CAM-02 (Tile 2)</option>
                <option value="2">CAM-03 (Tile 3)</option>
                <option value="3">CAM-04 (Tile 4)</option>
              </select>
            </div>

            <div>
              <label class="block text-slate-300 font-semibold mb-1">Camera Name / Label</label>
              <input type="text" id="modalCamName" placeholder="e.g. Public Traffic Cam / Warehouse Access" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-sky-500">
            </div>

            <div>
              <label class="block text-slate-300 font-semibold mb-1">Live Stream URL (HLS .m3u8, MP4, or Web Stream)</label>
              <input type="text" id="modalCamUrl" placeholder="https://.../playlist.m3u8 or /media/...mp4" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 font-mono text-[11px] focus:outline-none focus:border-sky-500">
            </div>

            <!-- Quick Presets -->
            <div>
              <span class="block text-slate-400 text-[11px] font-semibold mb-1.5">Quick Verified Streams:</span>
              <div class="flex flex-wrap gap-1.5">
                <button type="button" onclick="setModalPreset('Akamai 24/7 Live HLS Feed', 'https://cph-p2p-msl.akamaized.net/hls/live/2000341/test/master.m3u8')" class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 text-[10px]">
                  🌐 Akamai 24/7 Live HLS
                </button>
                <button type="button" onclick="setModalPreset('Public HD Test Feed', 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4')" class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[10px]">
                  🎥 Tears of Steel MP4
                </button>
                <button type="button" onclick="setModalPreset('Naivasha Gate CCTV Loop', '/media/gate_security.mp4')" class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-emerald-400 border border-slate-700 text-[10px]">
                  🏢 Gate CCTV Loop
                </button>
                <button type="button" onclick="setModalPreset('Naivasha Walkway CCTV Loop', '/media/pedestrian_walkway.mp4')" class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-emerald-400 border border-slate-700 text-[10px]">
                  🏢 Walkway CCTV Loop
                </button>
              </div>
            </div>

            <div class="bg-slate-950/80 border border-slate-800 rounded-lg p-3 text-[11px] text-slate-400 space-y-1">
              <p class="font-bold text-slate-300"><i class="fa-solid fa-circle-info text-sky-400 mr-1"></i> Testing Real Cameras:</p>
              <p>• <strong>Phone Camera:</strong> Use the free <em>IP Webcam</em> app (Android) or <em>RTSP Camera</em> (iOS) over Wi-Fi. Enter direct video URL: <code class="text-sky-300 font-mono">http://&lt;phone-ip&gt;:8080/video</code>.</p>
              <p>• <strong>RTSP Streams:</strong> Browsers require HLS or WebRTC. Raw <code class="text-sky-300 font-mono">rtsp://</code> streams are ingested on the Edge Appliance ("Aiota Box") via Frigate/go2rtc.</p>
            </div>
          </div>

          <div class="flex justify-end space-x-2 pt-2 border-t border-slate-800">
            <button onclick="closeCustomStreamModal()" class="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg transition">Cancel</button>
            <button onclick="applyCustomStream()" class="px-4 py-1.5 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-lg transition flex items-center space-x-1.5 shadow-lg shadow-sky-600/30">
              <i class="fa-solid fa-play text-[11px]"></i>
              <span>Apply & Stream</span>
            </button>
          </div>
        </div>
      </div>

      <!-- TAB 3: ALERTS -->
      <section id="viewAlerts" class="flex-1 overflow-y-auto p-6 hidden max-w-5xl space-y-6">
        <div>
          <h2 class="text-xl font-bold text-white flex items-center space-x-2">
            <i class="fa-brands fa-whatsapp text-emerald-400"></i>
            <span>Kenya WhatsApp & Multi-Channel Incident Router</span>
          </h2>
          <p class="text-xs text-slate-400 mt-1">Dispatches instant security snapshot cards & review clips directly to farm managers and logistics supervisors upon verified detection.</p>
        </div>

        <!-- 1. LIVE TEST CONSOLE -->
        <div class="bg-gradient-to-r from-emerald-950/40 via-slate-900 to-slate-900 border border-emerald-500/30 rounded-2xl p-5 shadow-xl">
          <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <span class="text-[10px] font-bold tracking-wider uppercase text-emerald-400 bg-emerald-950/80 border border-emerald-800/80 px-2 py-0.5 rounded">Real-Time Dispatch Tester</span>
              <h3 class="text-sm font-bold text-white mt-1.5">Test WhatsApp Incident Alert</h3>
              <p class="text-xs text-slate-400">Enter your Kenyan Safaricom/Airtel number to receive an immediate test security alert with a live CCTV snapshot.</p>
            </div>
            <div class="flex items-center space-x-2 w-full md:w-auto">
              <input type="text" id="alertTestPhone" value="+254 722 000 000" placeholder="+254 7..." class="bg-slate-950 border border-slate-700 text-white text-xs px-3 py-2 rounded-xl focus:border-emerald-500 focus:outline-none font-mono w-48" />
              <button onclick="triggerLiveTestAlert()" id="btnTestAlert" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-emerald-600/20 transition flex items-center space-x-1.5 whitespace-nowrap">
                <i class="fa-solid fa-paper-plane text-xs"></i>
                <span>Send Alert</span>
              </button>
            </div>
          </div>

          <!-- Alert Test Result Output (hidden until sent) -->
          <div id="testAlertResult" class="hidden mt-4 pt-4 border-t border-slate-800/80 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 bg-slate-950/80 p-3.5 rounded-xl border border-emerald-500/20">
            <div class="flex items-center space-x-3">
              <img id="testAlertSnap" src="/media/snap_highway_traffic.jpg" class="w-14 h-10 object-cover rounded-lg border border-slate-700 shadow" />
              <div>
                <div class="flex items-center space-x-2">
                  <span id="testAlertStatusBadge" class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">DISPATCHED</span>
                  <span id="testAlertRecipient" class="text-xs font-mono text-slate-300"></span>
                </div>
                <p id="testAlertNote" class="text-[11px] text-slate-400 mt-0.5"></p>
              </div>
            </div>
            <a id="testAlertWhatsAppLink" href="#" target="_blank" class="px-3.5 py-1.5 bg-emerald-700/80 hover:bg-emerald-600 text-white text-xs font-semibold rounded-lg flex items-center space-x-1.5 transition">
              <i class="fa-brands fa-whatsapp"></i>
              <span>Open in WhatsApp</span>
            </a>
          </div>
        </div>

        <!-- 2. ACTIVE ALERT RULES -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-bold text-white">Configured Alert Rules</h3>
              <p class="text-xs text-slate-400">Rules evaluated automatically on every edge detection event.</p>
            </div>
            <button onclick="openNewRuleModal()" class="px-3 py-1.5 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-xl transition flex items-center space-x-1.5">
              <i class="fa-solid fa-plus text-xs"></i>
              <span>New Alert Rule</span>
            </button>
          </div>

          <div id="alertRulesList" class="space-y-3">
            <div class="text-center py-6 text-slate-500 text-xs">Loading alert rules...</div>
          </div>
        </div>

        <!-- 3. RECENT DISPATCH AUDIT LOG -->
        <div class="space-y-3">
          <h3 class="text-sm font-bold text-white">Recent Alert Dispatch Log</h3>
          <div class="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th class="p-3">Time</th>
                  <th class="p-3">Rule / Trigger</th>
                  <th class="p-3">Recipient</th>
                  <th class="p-3">Channel</th>
                  <th class="p-3">Status</th>
                  <th class="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody id="alertLogsTableBody" class="divide-y divide-slate-800/80 text-slate-300">
                <tr><td colspan="6" class="p-4 text-center text-slate-500">Loading dispatch history...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- MODAL: CREATE ALERT RULE -->
      <div id="newRuleModal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm hidden flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
          <div class="flex justify-between items-center border-b border-slate-800 pb-3">
            <h3 class="font-bold text-white text-base flex items-center space-x-2">
              <i class="fa-brands fa-whatsapp text-emerald-400"></i>
              <span>Create WhatsApp Alert Rule</span>
            </h3>
            <button onclick="closeNewRuleModal()" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
          </div>

          <div class="space-y-3 text-xs">
            <div>
              <label class="block text-slate-300 font-semibold mb-1">Rule Name</label>
              <input type="text" id="ruleNameInput" placeholder="e.g. Fuel Depot Unauthorized Access" class="w-full bg-slate-950 border border-slate-700 text-white px-3 py-2 rounded-xl focus:border-sky-500 focus:outline-none" />
            </div>

            <div>
              <label class="block text-slate-300 font-semibold mb-1">Target Object Labels (comma separated)</label>
              <input type="text" id="ruleLabelsInput" value="person, vehicle, car, truck" placeholder="car, truck, person, livestock" class="w-full bg-slate-950 border border-slate-700 text-white px-3 py-2 rounded-xl font-mono focus:border-sky-500 focus:outline-none" />
              <p class="text-[10px] text-slate-500 mt-1">Available: person, vehicle, car, truck, livestock, horse, cow, dog</p>
            </div>

            <div>
              <label class="block text-slate-300 font-semibold mb-1">Minimum Confidence: <span id="ruleConfDisplay" class="text-sky-400 font-bold">75%</span></label>
              <input type="range" id="ruleConfSlider" min="50" max="95" value="75" oninput="document.getElementById('ruleConfDisplay').innerText = this.value + '%'" class="w-full accent-sky-400 cursor-pointer" />
            </div>

            <div>
              <label class="block text-slate-300 font-semibold mb-1">Recipient WhatsApp Phone Number</label>
              <input type="text" id="rulePhoneInput" value="+254 722 000 000" placeholder="+254 7XX XXX XXX" class="w-full bg-slate-950 border border-slate-700 text-white px-3 py-2 rounded-xl font-mono focus:border-emerald-500 focus:outline-none" />
            </div>
          </div>

          <div class="flex justify-end space-x-2 pt-3 border-t border-slate-800">
            <button onclick="closeNewRuleModal()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs rounded-xl transition">Cancel</button>
            <button onclick="submitNewAlertRule()" id="btnSaveRule" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-emerald-600/20 transition">Save & Activate</button>
          </div>
        </div>
      </div>

      <!-- TAB 4: APPLIANCES -->
      <section id="viewAppliances" class="flex-1 overflow-y-auto p-6 hidden max-w-4xl">
        <h2 class="text-lg font-bold text-white mb-2">On-Premise Aiota Appliances</h2>
        <p class="text-xs text-slate-400 mb-6">Intel N100 / Raspberry Pi AI appliances deployed across your client facilities.</p>

        <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th class="p-3">Appliance Name</th>
                <th class="p-3">Site Location</th>
                <th class="p-3">Inference Hardware</th>
                <th class="p-3">Status</th>
                <th class="p-3">Bearer Token</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800 text-slate-300">
              <tr>
                <td class="p-3 font-semibold text-white">Appliance-Alpha-N100</td>
                <td class="p-3">Naivasha Flower Ranch</td>
                <td class="p-3 font-mono">Intel N100 (OpenVINO)</td>
                <td class="p-3"><span class="text-emerald-400 font-bold bg-emerald-950/60 border border-emerald-800/50 px-2 py-0.5 rounded">ONLINE</span></td>
                <td class="p-3 font-mono text-slate-400">akilinova_edge_secret_token_12345</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </main>

    <!-- RIGHT INSPECTOR DRAWER -->
    <aside id="inspectorDrawer" class="w-80 border-l border-slate-800/80 bg-slate-900/90 backdrop-blur p-4 flex flex-col justify-between hidden shrink-0 z-20">
      <div>
        <div class="flex justify-between items-center mb-3 pb-3 border-b border-slate-800">
          <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Incident Inspector</span>
          <button onclick="closeInspector()" class="text-slate-400 hover:text-white p-1 rounded-lg">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>

        <div class="aspect-video bg-black rounded-lg overflow-hidden relative mb-3 border border-slate-800">
          <video id="drawerVideo" controls class="w-full h-full object-cover"></video>
          <img id="drawerImg" class="w-full h-full object-cover hidden" />
        </div>

        <div class="space-y-2.5 text-xs">
          <div>
            <span class="text-slate-500 block text-[10px] uppercase font-bold">Detection Label</span>
            <span id="drawerLabel" class="text-sm font-black text-white capitalize">---</span>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <span class="text-slate-500 block text-[10px] uppercase font-bold">Neural Confidence</span>
              <span id="drawerConfidence" class="font-mono text-sky-400 font-bold">---</span>
            </div>
            <div>
              <span class="text-slate-500 block text-[10px] uppercase font-bold">Similarity Match</span>
              <span id="drawerScore" class="font-mono text-emerald-400 font-bold">---</span>
            </div>
          </div>

          <div>
            <span class="text-slate-500 block text-[10px] uppercase font-bold">Camera Channel</span>
            <span id="drawerCamera" class="text-slate-200 font-medium">---</span>
          </div>

          <div>
            <span class="text-slate-500 block text-[10px] uppercase font-bold">Zone / Perimeter</span>
            <span id="drawerZone" class="text-slate-300 font-mono">---</span>
          </div>

          <div>
            <span class="text-slate-500 block text-[10px] uppercase font-bold">Timestamp (EAT UTC+3)</span>
            <span id="drawerTime" class="text-slate-400 font-mono text-[11px]">---</span>
          </div>
        </div>
      </div>

      <div class="space-y-2 pt-4 border-t border-slate-800">
        <a id="drawerDownload" href="#" download class="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg flex items-center justify-center space-x-2 border border-slate-700 transition">
          <i class="fa-solid fa-download"></i>
          <span>Export MP4 Clip</span>
        </a>
        <button onclick="shareWhatsApp()" class="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg flex items-center justify-center space-x-2 transition shadow-lg shadow-emerald-600/20">
          <i class="fa-brands fa-whatsapp text-sm"></i>
          <span>Share Incident via WhatsApp</span>
        </button>
      </div>
    </aside>
  </div>

  <script>
    let currentResults = [];
    let activeEvent = null;

    function setTab(tab) {
      ['search', 'wall', 'alerts', 'appliances'].forEach(t => {
        document.getElementById('view' + capitalize(t)).classList.add('hidden');
        document.getElementById('tabBtn' + capitalize(t)).className = 
          'w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 text-xs font-semibold transition';
      });

      document.getElementById('view' + capitalize(tab)).classList.remove('hidden');
      document.getElementById('tabBtn' + capitalize(tab)).className = 
        'w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sky-400 bg-sky-500/10 border border-sky-500/20 text-xs font-semibold transition';

      if (tab === 'alerts') {
        loadAlertRules();
        loadAlertLogs();
      }
    }

    function capitalize(str) {
      return str.charAt(0).toUpperCase() + str.slice(1);
    }

    async function fetchEvents(query = 'intruder coyote dog vehicle') {
      const grid = document.getElementById('resultsGrid');
      const counter = document.getElementById('statCounter');
      grid.innerHTML = '<div class="col-span-full py-16 text-center text-slate-500"><i class="fa-solid fa-circle-notch fa-spin text-3xl mb-2 text-sky-400"></i><p class="text-xs">Querying Qdrant Cloud Vector Database...</p></div>';

      try {
        const res = await fetch('/api/search', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ query_text: query, limit: 16 })
        });
        const data = await res.json();
        currentResults = data.results || [];
        counter.innerText = currentResults.length + ' Indexed Detection Events';

        if (currentResults.length === 0) {
          grid.innerHTML = `
            <div class="col-span-full py-16 text-center text-slate-500 border border-dashed border-slate-800 rounded-2xl">
              <i class="fa-solid fa-video-slash text-4xl mb-3 text-slate-600"></i>
              <p class="text-sm font-semibold text-slate-400">No detection incidents match your query.</p>
              <p class="text-xs text-slate-600 mt-1">Try searching for 'coyote', 'dog', 'intruder', or click 'Simulate Detection'.</p>
            </div>
          `;
          return;
        }

        grid.innerHTML = currentResults.map((ev, index) => {
          const matchPercent = Math.max(0, Math.round(ev.score * 100));
          const snap = ev.snapshot_url || 'https://placehold.co/600x400/0a0f1d/38bdf8?text=Detection+Snapshot';
          const hasClip = Boolean(ev.clip_url);

          return `
            <div onclick="inspectEvent(${index})" class="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden hover:border-sky-500/60 hover:shadow-xl hover:shadow-sky-500/5 transition duration-200 cursor-pointer flex flex-col group">
              <div class="relative aspect-video bg-black flex items-center justify-center overflow-hidden">
                <img src="${snap}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" />
                
                <span class="absolute top-2 right-2 text-[10px] font-black px-2 py-0.5 rounded bg-sky-950/90 text-sky-300 border border-sky-800/80 shadow">
                  ${matchPercent}% match
                </span>

                ${hasClip ? `
                  <div class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition duration-200">
                    <span class="w-10 h-10 rounded-full bg-sky-500 text-white flex items-center justify-center shadow-lg transform group-hover:scale-110 transition">
                      <i class="fa-solid fa-play ml-0.5 text-sm"></i>
                    </span>
                  </div>
                ` : ''}
                <span class="absolute bottom-1.5 left-2 text-[10px] bg-black/80 text-slate-300 px-1.5 py-0.5 rounded font-mono">
                  ${new Date(ev.started_at).toLocaleTimeString()}
                </span>
              </div>

              <div class="p-3.5 flex-1 flex flex-col justify-between">
                <div>
                  <div class="flex justify-between items-center mb-1">
                    <h3 class="font-bold capitalize text-white text-sm group-hover:text-sky-400 transition">${ev.primary_label}</h3>
                    <span class="text-[10px] font-mono text-slate-400 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800">${Math.round(ev.confidence * 100)}% conf</span>
                  </div>
                  <div class="flex items-center text-xs text-slate-400 space-x-1.5 mt-0.5">
                    <i class="fa-solid fa-camera text-sky-400 text-[10px]"></i>
                    <span class="truncate">${ev.camera_name}</span>
                  </div>
                </div>

                <div class="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
                  <span class="truncate font-mono">${ev.zones && ev.zones.length ? ev.zones[0] : 'perimeter'}</span>
                  ${hasClip ? '<span class="text-sky-400 font-semibold flex items-center"><i class="fa-solid fa-film mr-1 text-[10px]"></i>Review</span>' : '<span class="text-slate-600">Snapshot</span>'}
                </div>
              </div>
            </div>
          `;
        }).join('');
      } catch(e) {
        grid.innerHTML = '<div class="col-span-full py-8 text-center text-red-400 text-xs">Error querying vector index: ' + e.message + '</div>';
      }
    }

    function inspectEvent(index) {
      const ev = currentResults[index];
      if (!ev) return;
      activeEvent = ev;

      document.getElementById('drawerLabel').innerText = ev.primary_label;
      document.getElementById('drawerConfidence').innerText = Math.round(ev.confidence * 100) + '%';
      document.getElementById('drawerScore').innerText = Math.round(ev.score * 100) + '% match';
      document.getElementById('drawerCamera').innerText = ev.camera_name;
      document.getElementById('drawerZone').innerText = ev.zones && ev.zones.length ? ev.zones.join(', ') : 'perimeter';
      document.getElementById('drawerTime').innerText = new Date(ev.started_at).toLocaleString();

      const videoEl = document.getElementById('drawerVideo');
      const imgEl = document.getElementById('drawerImg');
      const dlBtn = document.getElementById('drawerDownload');

      if (ev.clip_url) {
        videoEl.classList.remove('hidden');
        imgEl.classList.add('hidden');
        videoEl.src = ev.clip_url;
        videoEl.play();
        dlBtn.href = ev.clip_url;
        dlBtn.classList.remove('opacity-50', 'pointer-events-none');
      } else {
        videoEl.pause();
        videoEl.classList.add('hidden');
        imgEl.classList.remove('hidden');
        imgEl.src = ev.snapshot_url;
        dlBtn.classList.add('opacity-50', 'pointer-events-none');
      }

      document.getElementById('inspectorDrawer').classList.remove('hidden');
    }

    function closeInspector() {
      const videoEl = document.getElementById('drawerVideo');
      videoEl.pause();
      document.getElementById('inspectorDrawer').classList.add('hidden');
    }

    function shareWhatsApp() {
      if (!activeEvent) return;
      const text = encodeURIComponent(`🚨 *AIOTA SECURITY ALERT* 🚨\\nIncident: ${activeEvent.primary_label.toUpperCase()}\\nCamera: ${activeEvent.camera_name}\\nConfidence: ${Math.round(activeEvent.confidence * 100)}%\\nTime: ${new Date(activeEvent.started_at).toLocaleString()}\\nReview: https://aiota.akilinova.co.ke/`);
      window.open(`https://api.whatsapp.com/send?text=${text}`, '_blank');
    }

    function quickSearch(q) {
      document.getElementById('searchQuery').value = q;
      fetchEvents(q);
    }

    async function triggerSimulatedDetection() {
      const btn = document.getElementById('btnSimulate');
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin text-sky-400"></i><span class="hidden md:inline">Simulating...</span>';
      btn.disabled = true;

      try {
        const labels = ['coyote predator', 'intruder person', 'stray dog', 'tractor vehicle'];
        const randomLabel = labels[Math.floor(Math.random() * labels.length)];
        const formData = new FormData();
        formData.append('edge_event_id', 'sim_evt_' + Math.random().toString(36).substring(2, 9));
        formData.append('camera_identifier', 'cam_gate_01');
        formData.append('primary_label', randomLabel);
        formData.append('confidence', (0.85 + Math.random() * 0.12).toFixed(2));
        formData.append('zones_entered', '["perimeter_zone"]');
        formData.append('detection_payload', '{"type": "edge_synthetic"}');
        formData.append('started_at', (Date.now() / 1000).toString());

        await fetch('/api/events/ingest', {
          method: 'POST',
          headers: { 'Authorization': 'Bearer akilinova_edge_secret_token_12345' },
          body: formData
        });

        setTimeout(() => {
          fetchEvents(document.getElementById('searchQuery').value || 'all');
          btn.innerHTML = '<i class="fa-solid fa-plus-circle text-sky-400"></i><span class="hidden md:inline">Simulate Detection</span>';
          btn.disabled = false;
        }, 1000);
      } catch (e) {
        alert('Simulation error: ' + e.message);
        btn.innerHTML = '<i class="fa-solid fa-plus-circle text-sky-400"></i><span class="hidden md:inline">Simulate Detection</span>';
        btn.disabled = false;
      }
    }

    document.getElementById('searchForm').addEventListener('submit', (e) => {
      e.preventDefault();
      const q = document.getElementById('searchQuery').value;
      fetchEvents(q.trim() || 'all');
    });

    // CAMERA WALL STREAM CONTROLLER
    const DEMO_PRESET = [
      { id: 0, title: 'CAM-01: Mombasa Road Highway Access', tag: 'RTSP-HWY-01', res: '1080p @ 30fps', url: '/media/clip_highway_traffic.mp4', badge: 'LIVE CCTV' },
      { id: 1, title: 'CAM-02: Commercial Turnstile & Crosswalk', tag: 'RTSP-XWALK-02', res: '1080p @ 24fps', url: '/media/clip_bikes_pedestrians.mp4', badge: 'LIVE CCTV' },
      { id: 2, title: 'CAM-03: Naivasha Flower Ranch Pasture', tag: 'RTSP-RANCH-03', res: '1080p @ 30fps', url: '/media/clip_farm_livestock.mp4', badge: 'LIVE CCTV' },
      { id: 3, title: 'CAM-04: Retail Store & Forecourt Till', tag: 'RTSP-RETAIL-04', res: '720p @ 15fps', url: '/media/clip_retail_checkout.mp4', badge: 'LIVE CCTV' }
    ];

    const PUBLIC_PRESET = [
      { id: 0, title: 'CAM-01: Akamai 24/7 Live HLS Stream', tag: 'LIVE-HLS-01', res: 'HLS Live Feed', url: 'https://cph-p2p-msl.akamaized.net/hls/live/2000341/test/master.m3u8', badge: 'LIVE HLS' },
      { id: 1, title: 'CAM-02: Public Highway Traffic Feed', tag: 'LIVE-PUB-02', res: '1080p Test', url: 'https://raw.githubusercontent.com/DeGirum/PySDKExamples/main/images/Traffic.mp4', badge: 'PUBLIC STREAM' },
      { id: 2, title: 'CAM-03: Public Pedestrians & Bikes Junction', tag: 'LIVE-PUB-03', res: '720p Test', url: 'https://raw.githubusercontent.com/DeGirum/PySDKExamples/main/images/aerial_crossing_pedestrians_bikes.mp4', badge: 'PUBLIC STREAM' },
      { id: 3, title: 'CAM-04: Public Facility Parking Yard', tag: 'LIVE-PUB-04', res: '720p Test', url: 'https://raw.githubusercontent.com/DeGirum/PySDKExamples/main/images/Parking.mp4', badge: 'PUBLIC STREAM' }
    ];

    let currentWallPreset = 'demo';
    const hlsInstances = {};

    function initCameraWall() {
      applyPreset(DEMO_PRESET);
    }

    function switchWallPreset(preset) {
      currentWallPreset = preset;
      const btnDemo = document.getElementById('btnPresetDemo');
      const btnPublic = document.getElementById('btnPresetPublic');
      const wallTitle = document.getElementById('wallTitle');
      const wallSubtitle = document.getElementById('wallSubtitle');

      if (preset === 'demo') {
        btnDemo.className = 'px-3 py-1 rounded-lg font-semibold bg-sky-500/20 text-sky-300 border border-sky-500/30 transition flex items-center space-x-1.5';
        btnPublic.className = 'px-3 py-1 rounded-lg font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition flex items-center space-x-1.5';
        wallTitle.innerText = 'Naivasha Flower Ranch - Live Camera Wall';
        wallSubtitle.innerText = 'Real on-premise surveillance loops over WebRTC / HLS buffer';
        applyPreset(DEMO_PRESET);
      } else {
        btnPublic.className = 'px-3 py-1 rounded-lg font-semibold bg-sky-500/20 text-sky-300 border border-sky-500/30 transition flex items-center space-x-1.5';
        btnDemo.className = 'px-3 py-1 rounded-lg font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition flex items-center space-x-1.5';
        wallTitle.innerText = 'Public Live CCTV & HLS Streams';
        wallSubtitle.innerText = 'Testing live external HLS & surveillance feeds from open internet';
        applyPreset(PUBLIC_PRESET);
      }
    }

    function applyPreset(presetArray) {
      presetArray.forEach(cfg => {
        playCameraTile(cfg.id, cfg.url, cfg.title, cfg.tag, cfg.res, cfg.badge);
      });
    }

    function playCameraTile(camIndex, url, title, tag, res, badge) {
      if (title) document.getElementById('camTitle' + camIndex).innerHTML = `<i class="fa-solid fa-camera mr-1 text-sky-400"></i>${title}`;
      if (tag) document.getElementById('camTag' + camIndex).innerText = tag;
      if (res) document.getElementById('camRes' + camIndex).innerText = res;
      if (badge) document.getElementById('camBadge' + camIndex).innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse mr-1.5"></span> ${badge}`;

      const video = document.getElementById('camVideo' + camIndex);
      if (!video) return;

      if (hlsInstances[camIndex]) {
        hlsInstances[camIndex].destroy();
        delete hlsInstances[camIndex];
      }

      if (url.includes('.m3u8')) {
        if (Hls.isSupported()) {
          const hls = new Hls({ enableWorker: true, lowLatencyMode: true });
          hls.loadSource(url);
          hls.attachMedia(video);
          hlsInstances[camIndex] = hls;
          hls.on(Hls.Events.MANIFEST_PARSED, function() {
            video.muted = true;
            video.play().catch(e => console.log('Autoplay info:', e));
          });
          hls.on(Hls.Events.ERROR, function(event, data) {
            if (data.fatal) {
              console.warn('HLS fatal error on cam', camIndex, data);
            }
          });
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
          video.src = url;
          video.muted = true;
          video.play().catch(e => console.log('Autoplay info:', e));
        }
      } else {
        video.src = url;
        video.muted = true;
        video.play().catch(e => console.log('Autoplay info:', e));
      }
    }

    function openCustomStreamModal(slot = 0) {
      document.getElementById('modalCamSelect').value = slot;
      const currentTitle = document.getElementById('camTitle' + slot).innerText.trim();
      const currentVideo = document.getElementById('camVideo' + slot);
      document.getElementById('modalCamName').value = currentTitle;
      document.getElementById('modalCamUrl').value = currentVideo.src || '';
      document.getElementById('streamModal').classList.remove('hidden');
    }

    function closeCustomStreamModal() {
      document.getElementById('streamModal').classList.add('hidden');
    }

    function setModalPreset(name, url) {
      document.getElementById('modalCamName').value = name;
      document.getElementById('modalCamUrl').value = url;
    }

    function applyCustomStream() {
      const slot = parseInt(document.getElementById('modalCamSelect').value, 10);
      const name = document.getElementById('modalCamName').value.trim() || `Custom Stream CAM-0${slot + 1}`;
      const url = document.getElementById('modalCamUrl').value.trim();

      if (!url) {
        alert('Please enter a valid Stream URL (e.g. .m3u8 or .mp4 or HTTP feed)');
        return;
      }

      const isHls = url.includes('.m3u8');
      playCameraTile(slot, url, name, 'CUSTOM-0' + (slot + 1), isHls ? 'HLS Stream' : 'Live Feed', isHls ? 'LIVE HLS' : 'CUSTOM FEED');
      closeCustomStreamModal();
    }

    // ALERT RULES & DISPATCH CONTROLLER
    async function loadAlertRules() {
      const container = document.getElementById('alertRulesList');
      if (!container) return;
      try {
        const res = await fetch('/api/alerts/rules');
        const rules = await res.json();
        if (!rules || rules.length === 0) {
          container.innerHTML = '<div class="text-center py-6 text-slate-500 text-xs">No active alert rules configured yet. Click "+ New Alert Rule" to add one.</div>';
          return;
        }
        container.innerHTML = rules.map(r => `
          <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-slate-700 transition">
            <div>
              <div class="flex items-center space-x-2">
                <span class="font-bold text-sm text-white">${r.name}</span>
                <span class="text-[10px] ${r.is_active ? 'bg-emerald-950 text-emerald-400 border-emerald-800/60' : 'bg-slate-800 text-slate-400'} border px-2 py-0.5 rounded font-semibold">${r.is_active ? 'Active' : 'Disabled'}</span>
                <span class="text-[10px] font-mono text-sky-400 bg-sky-950/60 border border-sky-800/40 px-2 py-0.5 rounded">&ge; ${Math.round(r.min_confidence * 100)}% conf</span>
              </div>
              <p class="text-xs text-slate-400 mt-1">Triggers when <span class="text-sky-300 font-mono">${(r.target_labels || []).join(' / ')}</span> detected across <span class="text-slate-300 font-semibold">${r.site_name}</span>.</p>
              <div class="text-[11px] text-slate-400 mt-2 flex items-center space-x-4">
                <span><i class="fa-brands fa-whatsapp text-emerald-400 mr-1.5"></i>${r.phone_number || 'Default Dispatch'}</span>
                <span class="text-slate-500"><i class="fa-solid fa-clock text-[10px] mr-1"></i>24/7 Real-Time</span>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button onclick="quickTestRule('${r.phone_number}')" class="px-3 py-1.5 bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800/60 text-xs font-semibold rounded-lg transition flex items-center space-x-1">
                <i class="fa-solid fa-bolt text-[10px]"></i>
                <span>Test Ping</span>
              </button>
            </div>
          </div>
        `).join('');
      } catch(e) {
        container.innerHTML = '<div class="text-center py-6 text-red-400 text-xs">Error loading alert rules: ' + e.message + '</div>';
      }
    }

    async function loadAlertLogs() {
      const tbody = document.getElementById('alertLogsTableBody');
      if (!tbody) return;
      try {
        const res = await fetch('/api/alerts/logs?limit=10');
        const logs = await res.json();
        if (!logs || logs.length === 0) {
          tbody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-slate-500">No alerts dispatched yet. Send a test alert above to verify!</td></tr>';
          return;
        }
        tbody.innerHTML = logs.map(l => {
          const isSent = l.status === 'sent';
          const isSim = l.status === 'simulated';
          const badgeClass = isSent ? 'bg-emerald-950 text-emerald-400 border-emerald-800' :
                             isSim ? 'bg-sky-950 text-sky-400 border-sky-800' : 'bg-red-950 text-red-400 border-red-800';
          const badgeText = isSent ? 'SENT (LIVE)' : isSim ? 'DISPATCHED (SANDBOX)' : 'FAILED';
          const timeStr = new Date(l.created_at).toLocaleTimeString();

          return `
            <tr class="hover:bg-slate-800/40 transition">
              <td class="p-3 font-mono text-[11px] text-slate-400">${timeStr}</td>
              <td class="p-3 font-semibold text-white">${l.rule_name}</td>
              <td class="p-3 font-mono text-slate-300">${l.recipient}</td>
              <td class="p-3 capitalize"><i class="fa-brands fa-whatsapp text-emerald-400 mr-1"></i>${l.channel}</td>
              <td class="p-3"><span class="text-[10px] font-bold px-2 py-0.5 rounded border ${badgeClass}">${badgeText}</span></td>
              <td class="p-3 text-right">
                ${l.click_to_chat_url ? `
                  <a href="${l.click_to_chat_url}" target="_blank" class="px-2.5 py-1 bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 border border-emerald-500/30 rounded text-[11px] font-semibold transition inline-flex items-center space-x-1">
                    <i class="fa-brands fa-whatsapp"></i><span>View</span>
                  </a>
                ` : `<span class="text-slate-600 text-[11px]">Logged</span>`}
              </td>
            </tr>
          `;
        }).join('');
      } catch(e) {
        tbody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-red-400">Error loading alert logs: ' + e.message + '</td></tr>';
      }
    }

    async function triggerLiveTestAlert() {
      const phone = document.getElementById('alertTestPhone').value.trim();
      const btn = document.getElementById('btnTestAlert');
      const resultBox = document.getElementById('testAlertResult');
      if (!phone) {
        alert('Please enter a valid phone number (e.g. +254 7XX XXX XXX)');
        return;
      }

      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1"></i> Sending...';

      try {
        const res = await fetch('/api/alerts/test', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ phone_number: phone, channel: 'whatsapp' })
        });
        const data = await res.json();

        resultBox.classList.remove('hidden');
        document.getElementById('testAlertRecipient').innerText = data.recipient;
        document.getElementById('testAlertNote').innerText = data.is_live_gateway ? 
          'Dispatched live via Meta / Twilio WhatsApp gateway!' : 
          'Security snapshot card generated! Click below to open preview in WhatsApp.';
        document.getElementById('testAlertWhatsAppLink').href = data.click_to_chat_url;
        document.getElementById('testAlertSnap').src = data.snapshot_url;

        loadAlertLogs();
      } catch(e) {
        alert('Alert dispatch failed: ' + e.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-paper-plane text-xs mr-1"></i> Send Alert';
      }
    }

    function quickTestRule(phone) {
      if (phone) document.getElementById('alertTestPhone').value = phone;
      triggerLiveTestAlert();
    }

    function openNewRuleModal() {
      document.getElementById('newRuleModal').classList.remove('hidden');
    }

    function closeNewRuleModal() {
      document.getElementById('newRuleModal').classList.add('hidden');
    }

    async function submitNewAlertRule() {
      const name = document.getElementById('ruleNameInput').value.trim();
      const labelsRaw = document.getElementById('ruleLabelsInput').value.trim();
      const phone = document.getElementById('rulePhoneInput').value.trim();
      const conf = parseInt(document.getElementById('ruleConfSlider').value, 10) / 100;

      if (!name || !phone) {
        alert('Please provide both Rule Name and Phone Number');
        return;
      }

      const labels = labelsRaw.split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
      const btn = document.getElementById('btnSaveRule');
      btn.disabled = true;
      btn.innerText = 'Saving...';

      try {
        const res = await fetch('/api/alerts/rules', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            name: name,
            target_labels: labels,
            min_confidence: conf,
            phone_number: phone
          })
        });
        if (!res.ok) throw new Error('Server returned ' + res.status);
        closeNewRuleModal();
        loadAlertRules();
      } catch(e) {
        alert('Failed saving rule: ' + e.message);
      } finally {
        btn.disabled = false;
        btn.innerText = 'Save & Activate';
      }
    }

    fetchEvents('all');
    initCameraWall();
  </script>
</body>
</html>"""

def favicon_view(request):
    return HttpResponse(FAVICON_SVG, content_type='image/svg+xml')

@csrf_exempt
def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/console'
    if request.user.is_authenticated:
        return HttpResponseRedirect(next_url)

    error_block = ""
    if request.method == 'POST':
        u = (request.POST.get('username') or '').strip()
        p = (request.POST.get('password') or '').strip()
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(next_url)
        else:
            error_block = """
            <div class="bg-red-950/80 border border-red-800/80 text-red-200 text-xs px-3.5 py-2.5 rounded-xl flex items-center space-x-2">
              <i class="fa-solid fa-circle-exclamation text-red-400 text-sm"></i>
              <span>Invalid username or password. Please verify credentials.</span>
            </div>
            """

    page = LOGIN_HTML_TEMPLATE.replace('{ERROR_MESSAGE_BLOCK}', error_block)
    return HttpResponse(page)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login')

def get_demo_cameras_api(request):
    cameras = Camera.objects.filter(is_active=True).values('id', 'name', 'identifier', 'demo_video_url')
    return JsonResponse({'cameras': list(cameras)})

def landing_view(request):
    """Public high-converting marketing landing page for Kenya & East Africa."""
    if request.user.is_authenticated:
        auth_nav = (
            f'<a href="/console" class="text-xs font-bold text-sky-400 bg-sky-950/80 border border-sky-800/80 px-3.5 py-1.5 rounded-xl hover:bg-sky-900 transition flex items-center space-x-2">'
            f'<i class="fa-solid fa-desktop text-xs"></i><span>Console ({request.user.username})</span></a>'
        )
    else:
        auth_nav = '<a href="/login" class="text-xs font-bold text-slate-300 hover:text-white px-3.5 py-1.5 rounded-xl hover:bg-slate-900 transition">Sign In</a>'

    html = MARKETING_HTML.replace('{AUTH_NAV_BUTTONS}', auth_nav)
    return HttpResponse(html)

def console_view(request):
    """Authenticated enterprise surveillance & AI intelligence console."""
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login?next=/console')

    member = OrganizationMember.objects.filter(user=request.user).select_related('organization').first()
    org_name = member.organization.name if member else 'Akilinova Vision'
    role_label = member.get_role_display() if member else 'SuperAdmin'

    html = DASHBOARD_AUTH_HTML.replace('{ORG_NAME}', org_name).replace('{USERNAME}', request.user.username).replace('{ROLE}', role_label)
    return HttpResponse(html)

@csrf_exempt
def lead_capture_view(request):
    """Captures pilot & demo requests from the marketing page."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else {}
        except Exception:
            data = request.POST.dict()

        # Log lead submission
        log_line = f"[{request.META.get('REMOTE_ADDR')}] {data}\n"
        log_file = getattr(settings, 'BASE_DIR', '.') / 'leads.log'
        try:
            with open(log_file, 'a') as f:
                f.write(log_line)
        except Exception:
            pass

        return JsonResponse({'status': 'ok', 'message': 'Lead received successfully'})
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

urlpatterns = [
    path('api/', api.urls),
    path('favicon.ico', favicon_view),
    path('login', login_view),
    path('logout', logout_view),
    path('console', console_view),
    path('dashboard', console_view),
    path('app', console_view),
    path('api/lead-capture', lead_capture_view),
    path('api/demo-cameras', get_demo_cameras_api),
    path('', landing_view),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
