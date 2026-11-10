import json
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from app.api.endpoints import api
from app.core.models import Organization, OrganizationMember, Camera, DetectionEvent

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en" class="h-full bg-slate-950">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Login | Aiota Video Intelligence</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="h-full bg-[#070b14] flex items-center justify-center p-4 antialiased text-slate-100">
  <div class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
    <div class="p-8 border-b border-slate-800 bg-slate-950/40 text-center">
      <div class="w-12 h-12 rounded-xl bg-sky-500/20 text-sky-400 flex items-center justify-center font-black text-2xl border border-sky-500/30 mx-auto mb-3 shadow-inner">
        <i class="fa-solid fa-eye"></i>
      </div>
      <h1 class="text-xl font-black tracking-wider text-white">AIOTA ENTERPRISE</h1>
      <p class="text-xs text-slate-400 mt-1 font-medium">Kenya Video Intelligence & Security Platform</p>
    </div>

    <form method="POST" action="/login" class="p-8 space-y-4">
      <div id="errorBox" class="hidden bg-red-950/80 border border-red-800/80 text-red-200 text-xs p-3 rounded-xl"></div>

      <div>
        <label class="block text-xs font-bold uppercase text-slate-400 mb-1.5">Username / Email</label>
        <div class="relative">
          <i class="fa-solid fa-user absolute left-3.5 top-3.5 text-slate-500 text-xs"></i>
          <input type="text" name="username" required placeholder="admin" value="admin"
            class="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-600 focus:outline-none focus:border-sky-500 transition" />
        </div>
      </div>

      <div>
        <label class="block text-xs font-bold uppercase text-slate-400 mb-1.5">Password</label>
        <div class="relative">
          <i class="fa-solid fa-lock absolute left-3.5 top-3.5 text-slate-500 text-xs"></i>
          <input type="password" name="password" required placeholder="••••••••" value="Admin@Akilinova2026!"
            class="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-600 focus:outline-none focus:border-sky-500 transition" />
        </div>
      </div>

      <div class="pt-2">
        <button type="submit" class="w-full py-3 bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold uppercase tracking-wider rounded-xl transition shadow-lg shadow-sky-600/25 flex items-center justify-center space-x-2">
          <span>Sign In to Platform</span>
          <i class="fa-solid fa-arrow-right text-xs"></i>
        </button>
      </div>

      <div class="text-center pt-2">
        <span class="text-[11px] text-slate-500">Default demo: <strong class="text-slate-400 font-mono">admin</strong> / <strong class="text-slate-400 font-mono">Admin@Akilinova2026!</strong></span>
      </div>
    </form>
  </div>
</body>
</html>"""

DASHBOARD_AUTH_HTML = """<!DOCTYPE html>
<html lang="en" class="h-full bg-slate-950">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aiota Enterprise | Video Intelligence Platform</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
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
          <i class="fa-solid fa-eye text-sm"></i>
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
            <button onclick="quickSearch('intruder person near gate')" class="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/60 shrink-0 transition">
              🚨 Perimeter Intruder
            </button>
            <button onclick="quickSearch('coyote predator near pasture')" class="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/60 shrink-0 transition">
              🐺 Predator / Rustling
            </button>
            <button onclick="quickSearch('tractor vehicle in feedlot')" class="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/60 shrink-0 transition">
              🚜 Farm Vehicles
            </button>
            <button onclick="quickSearch('stray dog fence')" class="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/60 shrink-0 transition">
              🐕 Stray Animal
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

      <!-- TAB 2: LIVE CAMERA WALL (REAL WORKING VIDEOS FOR DEMO) -->
      <section id="viewWall" class="flex-1 flex flex-col overflow-hidden hidden p-4">
        <div class="flex justify-between items-center mb-3">
          <div>
            <h2 class="text-base font-bold text-white flex items-center space-x-2">
              <i class="fa-solid fa-table-cells text-sky-400"></i>
              <span>Naivasha Flower Ranch - Live Camera Wall</span>
            </h2>
            <p class="text-xs text-slate-400">Live video streaming over WebRTC / HLS local buffer</p>
          </div>
          <span class="text-xs text-emerald-400 bg-emerald-950/60 border border-emerald-800/50 px-2.5 py-1 rounded-lg flex items-center">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping mr-2"></span> 4 Streams Online
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1 overflow-y-auto" id="cameraWallGrid">
          <!-- Cam 1 -->
          <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
            <div class="p-2.5 bg-slate-950 border-b border-slate-800 flex justify-between items-center text-xs font-semibold">
              <span class="text-slate-200"><i class="fa-solid fa-camera mr-1 text-sky-400"></i>CAM-01: North Perimeter Gate</span>
              <span class="text-[10px] text-emerald-400 font-mono">1080p @ 15fps</span>
            </div>
            <div class="flex-1 bg-black relative aspect-video flex items-center justify-center">
              <video src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" autoplay loop muted playsinline class="w-full h-full object-cover"></video>
              <div class="absolute bottom-2 left-2 text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-mono font-bold flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse mr-1.5"></span> LIVE FEED
              </div>
            </div>
          </div>

          <!-- Cam 2 -->
          <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
            <div class="p-2.5 bg-slate-950 border-b border-slate-800 flex justify-between items-center text-xs font-semibold">
              <span class="text-slate-200"><i class="fa-solid fa-camera mr-1 text-sky-400"></i>CAM-02: Livestock Feedlot</span>
              <span class="text-[10px] text-emerald-400 font-mono">1080p @ 15fps</span>
            </div>
            <div class="flex-1 bg-black relative aspect-video flex items-center justify-center">
              <video src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4" autoplay loop muted playsinline class="w-full h-full object-cover"></video>
              <div class="absolute bottom-2 left-2 text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-mono font-bold flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse mr-1.5"></span> LIVE FEED
              </div>
            </div>
          </div>

          <!-- Cam 3 -->
          <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
            <div class="p-2.5 bg-slate-950 border-b border-slate-800 flex justify-between items-center text-xs font-semibold">
              <span class="text-slate-200"><i class="fa-solid fa-camera mr-1 text-sky-400"></i>CAM-03: Greenhouse Rose Perimeter</span>
              <span class="text-[10px] text-emerald-400 font-mono">1080p @ 15fps</span>
            </div>
            <div class="flex-1 bg-black relative aspect-video flex items-center justify-center">
              <video src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4" autoplay loop muted playsinline class="w-full h-full object-cover"></video>
              <div class="absolute bottom-2 left-2 text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-mono font-bold flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse mr-1.5"></span> LIVE FEED
              </div>
            </div>
          </div>

          <!-- Cam 4 -->
          <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
            <div class="p-2.5 bg-slate-950 border-b border-slate-800 flex justify-between items-center text-xs font-semibold">
              <span class="text-slate-200"><i class="fa-solid fa-camera mr-1 text-sky-400"></i>CAM-04: Fuel Depot & Machinery Yard</span>
              <span class="text-[10px] text-emerald-400 font-mono">1080p @ 15fps</span>
            </div>
            <div class="flex-1 bg-black relative aspect-video flex items-center justify-center">
              <video src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4" autoplay loop muted playsinline class="w-full h-full object-cover"></video>
              <div class="absolute bottom-2 left-2 text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-mono font-bold flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse mr-1.5"></span> LIVE FEED
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB 3: ALERTS -->
      <section id="viewAlerts" class="flex-1 overflow-y-auto p-6 hidden max-w-4xl">
        <h2 class="text-lg font-bold text-white mb-2">Kenya WhatsApp & SMS Incident Router</h2>
        <p class="text-xs text-slate-400 mb-6">Dispatches instant snapshot cards to farm managers & security dispatch via WhatsApp upon verified tripwire breach.</p>

        <div class="space-y-4">
          <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
            <div>
              <div class="flex items-center space-x-2">
                <span class="font-bold text-sm text-white">Naivasha Night Predator Alert</span>
                <span class="text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800/60 px-2 py-0.5 rounded font-semibold">Active</span>
              </div>
              <p class="text-xs text-slate-400 mt-1">Triggers when <span class="text-sky-300 font-mono">coyote / hyena / intruder</span> detected in <span class="text-slate-300">gate_perimeter</span> between 19:00 - 06:00.</p>
              <div class="text-[11px] text-slate-500 mt-2 flex items-center space-x-3">
                <span><i class="fa-brands fa-whatsapp text-emerald-400 mr-1"></i>+254 712 *** 890 (Farm Manager)</span>
                <span><i class="fa-solid fa-comment-sms text-sky-400 mr-1"></i>Safaricom SMS Backup</span>
              </div>
            </div>
            <button class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-semibold rounded-lg border border-slate-700 text-slate-200">
              Edit Rule
            </button>
          </div>
        </div>
      </section>

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

    fetchEvents('coyote intruder dog vehicle');
  </script>
</body>
</html>"""

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            err_html = LOGIN_HTML.replace('class="hidden bg-red-950', 'class="block bg-red-950').replace('</div>', 'Invalid credentials. Please verify username and password.</div>', 1)
            return HttpResponse(err_html)

    return HttpResponse(LOGIN_HTML)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login')

def get_demo_cameras_api(request):
    cameras = Camera.objects.filter(is_active=True).values('id', 'name', 'identifier', 'demo_video_url')
    return JsonResponse({'cameras': list(cameras)})

def home_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')

    member = OrganizationMember.objects.filter(user=request.user).select_related('organization').first()
    org_name = member.organization.name if member else 'Akilinova Vision'
    role_label = member.get_role_display() if member else 'SuperAdmin'

    html = DASHBOARD_AUTH_HTML.replace('{ORG_NAME}', org_name).replace('{USERNAME}', request.user.username).replace('{ROLE}', role_label)
    return HttpResponse(html)

urlpatterns = [
    path('api/', api.urls),
    path('login', login_view),
    path('logout', logout_view),
    path('api/demo-cameras', get_demo_cameras_api),
    path('', home_view),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
