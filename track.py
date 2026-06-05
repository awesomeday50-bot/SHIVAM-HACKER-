import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask, request, render_template_string
import requests
import re

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SHIVAM HACKER // NUMBER TRACKER</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
<style>

:root {
  --g:    #00ff41;
  --gdim: #00cc33;
  --gbg:  rgba(0,255,65,0.07);
  --gborder: rgba(0,255,65,0.3);
  --bg:   #030f03;
  --card: #060f06;
  --text: #c8ffd4;
}

* { margin:0; padding:0; box-sizing:border-box; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'JetBrains Mono', monospace;
  min-height: 100vh;
  overflow-x: hidden;
}

/* ── MATRIX CANVAS ── */
#mc {
  position: fixed; top:0; left:0;
  width:100%%; height:100%%;
  z-index: 0; opacity: 0.12;
  pointer-events: none;
}

/* all content above canvas */
.wrap { position: relative; z-index: 1; }

/* ── HEADER ── */
.hdr {
  text-align: center;
  padding: 28px 16px 12px;
  border-bottom: 1px solid var(--gborder);
  background: rgba(0,0,0,0.55);
  backdrop-filter: blur(6px);
}
.hdr-sub {
  font-size: 11px;
  letter-spacing: 5px;
  color: var(--gdim);
  margin-bottom: 6px;
}
.hdr-title {
  font-family: 'Orbitron', sans-serif;
  font-size: clamp(20px, 4.5vw, 38px);
  font-weight: 900;
  color: var(--g);
  letter-spacing: 3px;
  text-shadow: 0 0 8px var(--g), 0 0 24px rgba(0,255,65,0.4);
}
.hdr-badge {
  display: inline-flex;
  gap: 18px;
  margin-top: 10px;
  font-size: 10px;
  letter-spacing: 3px;
  color: var(--gdim);
}
.dot {
  width:7px; height:7px;
  border-radius:50%%;
  background: var(--g);
  display:inline-block;
  margin-right:5px;
  box-shadow: 0 0 5px var(--g);
  animation: blink 1.4s infinite;
}
@keyframes blink { 0%%,100%% {opacity:1} 50%% {opacity:0.25} }

/* ── CONTAINER ── */
.box {
  width: 94%%;
  max-width: 580px;
  margin: 0 auto;
  padding: 18px 0 50px;
}

/* ── CARD ── */
.card {
  background: var(--card);
  border: 1px solid var(--gborder);
  border-radius: 8px;
  padding: 24px;
  margin-top: 20px;
  box-shadow: 0 0 24px rgba(0,255,65,0.06);
}
.card-lbl {
  font-size: 10px;
  letter-spacing: 4px;
  color: var(--gdim);
  margin-bottom: 14px;
  opacity: 0.75;
}
.card-lbl::before { content:"// "; opacity:0.5; }

/* ── INPUT ── */
input[type=text] {
  width: 100%%;
  padding: 15px 18px;
  background: rgba(0,255,65,0.05);
  border: 1.5px solid rgba(0,255,65,0.4);
  border-radius: 6px;
  color: #ffffff;
  font-family: 'JetBrains Mono', monospace;
  font-size: 18px;
  letter-spacing: 5px;
  text-align: center;
  outline: none;
  transition: 0.25s;
}
input[type=text]:focus {
  border-color: var(--g);
  background: rgba(0,255,65,0.09);
  box-shadow: 0 0 18px rgba(0,255,65,0.2);
}
input::placeholder { color: rgba(0,255,65,0.3); letter-spacing:3px; }

/* ── BUTTON ── */
.btn-track {
  width: 100%%;
  padding: 15px;
  margin-top: 14px;
  background: rgba(0,255,65,0.08);
  border: 1.5px solid var(--g);
  border-radius: 6px;
  color: var(--g);
  font-family: 'Orbitron', sans-serif;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 4px;
  cursor: pointer;
  transition: 0.25s;
}
.btn-track:hover {
  background: rgba(0,255,65,0.18);
  box-shadow: 0 0 22px rgba(0,255,65,0.35);
  transform: translateY(-1px);
}
.btn-track:active { transform: scale(0.98); }

/* ── RESULT SECTION HEADER ── */
.res-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--gborder);
}
.res-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 14px;
  letter-spacing: 3px;
  color: var(--g);
  text-shadow: 0 0 8px rgba(0,255,65,0.5);
}

/* ── COPY ALL BUTTON ── */
.btn-copy {
  padding: 8px 16px;
  background: rgba(0,255,65,0.1);
  border: 1px solid var(--g);
  border-radius: 5px;
  color: var(--g);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 2px;
  cursor: pointer;
  transition: 0.2s;
  white-space: nowrap;
}
.btn-copy:hover {
  background: rgba(0,255,65,0.22);
  box-shadow: 0 0 14px rgba(0,255,65,0.3);
}
.btn-copy.copied {
  background: rgba(0,255,65,0.3);
  color: #fff;
}

/* ── DATA ROWS ── */
.row {
  display: grid;
  grid-template-columns: 140px 1fr;
  align-items: start;
  gap: 8px 14px;
  padding: 13px 0;
  border-bottom: 1px solid rgba(0,255,65,0.1);
}
.row:last-of-type { border-bottom: none; }

.row-lbl {
  font-size: 11px;
  letter-spacing: 2px;
  color: var(--gdim);
  padding-top: 2px;
  opacity: 0.85;
}
.row-val {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  line-height: 1.5;
  word-break: break-word;
}

/* Aadhaar masking look */
.aadhaar-val {
  letter-spacing: 4px;
  font-size: 15px;
}

/* ── MAP ── */
#map {
  height: 280px;
  border-radius: 7px;
  margin-top: 16px;
  border: 1px solid rgba(0,255,65,0.3);
  box-shadow: 0 0 18px rgba(0,255,65,0.08);
  filter: hue-rotate(95deg) saturate(0.65) brightness(0.82);
}
#dist-lbl {
  margin-top: 12px;
  text-align: center;
  font-size: 15px;
  color: var(--g);
  letter-spacing: 2px;
}

/* ── TOAST ── */
.toast {
  position: fixed;
  bottom: 28px; left: 50%%;
  transform: translateX(-50%%);
  background: rgba(0,255,65,0.18);
  border: 1px solid var(--g);
  color: var(--g);
  padding: 10px 26px;
  border-radius: 40px;
  font-size: 13px;
  letter-spacing: 2px;
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 9999;
  pointer-events: none;
}
.toast.show { opacity: 1; }

/* ── FOOTER ── */
.ftr {
  text-align: center;
  margin-top: 32px;
  font-size: 11px;
  color: rgba(0,255,65,0.35);
  letter-spacing: 3px;
}
.ftr span { color: var(--g); }

</style>
</head>
<body>

<canvas id="mc"></canvas>

<div class="wrap">

<!-- HEADER -->
<div class="hdr">
  <div class="hdr-sub">DEV :: SHIVAM HACKER</div>
  <div class="hdr-title">☠ SHIVAM HACKER ☠</div>
  <div class="hdr-badge">
    <span><span class="dot"></span>ONLINE</span>
    <span><span class="dot"></span>SECURE</span>
    <span><span class="dot"></span>ANONYMOUS</span>
  </div>
</div>

<!-- MAIN -->
<div class="box">

  <!-- INPUT CARD -->
  <div class="card">
    <div class="card-lbl">TARGET NUMBER INPUT</div>
    <form method="POST">
      <input type="text" name="number" placeholder="ENTER MOBILE NUMBER" required autocomplete="off" id="numInput">
      <button type="submit" class="btn-track">⚡ TRACK NOW ⚡</button>
    </form>
  </div>

  <!-- RESULT CARD -->
  {% if data %}
  <div class="card" id="resultCard">

    <div class="res-head">
      <div class="res-title">⚡ TARGET INFO</div>
      <button class="btn-copy" onclick="copyAll()" id="copyBtn">📋 COPY ALL</button>
    </div>

    <div class="row">
      <span class="row-lbl">👤 NAME</span>
      <span class="row-val">{{ data.name }}</span>
    </div>

    {% if data.fname and data.fname != 'N/A' %}
    <div class="row">
      <span class="row-lbl">👨 FATHER</span>
      <span class="row-val">{{ data.fname }}</span>
    </div>
    {% endif %}

    <div class="row">
      <span class="row-lbl">📱 MOBILE</span>
      <span class="row-val">{{ data.mobile }}</span>
    </div>

    {% if data.alt and data.alt != 'N/A' %}
    <div class="row">
      <span class="row-lbl">📲 ALT NUM</span>
      <span class="row-val">{{ data.alt }}</span>
    </div>
    {% endif %}

    {% if data.circle and data.circle != 'N/A' %}
    <div class="row">
      <span class="row-lbl">📡 CIRCLE</span>
      <span class="row-val">{{ data.circle }}</span>
    </div>
    {% endif %}

    {% if data.email and data.email != 'N/A' %}
    <div class="row">
      <span class="row-lbl">📧 EMAIL</span>
      <span class="row-val">{{ data.email }}</span>
    </div>
    {% endif %}

    <div class="row">
      <span class="row-lbl">🏠 ADDRESS</span>
      <span class="row-val" id="addrVal">{{ data.address }}</span>
    </div>

    {% if data.aadhaar and data.aadhaar != 'N/A' %}
    <div class="row">
      <span class="row-lbl">🪪 AADHAAR</span>
      <span class="row-val aadhaar-val">{{ data.aadhaar }}</span>
    </div>
    {% endif %}

    <div id="map"></div>
    <div id="dist-lbl"></div>

  </div>
  {% endif %}

</div>

<!-- FOOTER -->
<div class="ftr">CODED BY <span>SHIVAM HACKER</span> &nbsp;|&nbsp; ALL RIGHTS RESERVED &nbsp;|&nbsp; <span>☠</span></div>

</div><!-- /wrap -->

<!-- TOAST -->
<div class="toast" id="toast">✅ DATA COPIED!</div>

<script>
// ── MATRIX RAIN ──────────────────────────────────────
const cv = document.getElementById('mc');
const cx = cv.getContext('2d');
function resize(){ cv.width=innerWidth; cv.height=innerHeight; }
resize(); window.addEventListener('resize', resize);
const CH = "SHIVAM0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%%^&*<>?";
const FS = 14;
let cols, drops;
function initDrops(){ cols=Math.floor(cv.width/FS); drops=Array.from({length:cols},()=>Math.random()*-80); }
initDrops(); window.addEventListener('resize', initDrops);
function rain(){
  cx.fillStyle="rgba(3,15,3,0.06)";
  cx.fillRect(0,0,cv.width,cv.height);
  for(let i=0;i<drops.length;i++){
    cx.fillStyle = Math.random()>0.96?"#ffffff":"#00ff41";
    cx.font=FS+"px monospace";
    cx.fillText(CH[Math.floor(Math.random()*CH.length)], i*FS, drops[i]*FS);
    if(drops[i]*FS>cv.height && Math.random()>0.975) drops[i]=0;
    drops[i]++;
  }
}
setInterval(rain,50);

// ── COPY ALL ─────────────────────────────────────────
function copyAll(){
  const rows = document.querySelectorAll('#resultCard .row');
  let text = "=== SHIVAM HACKER - NUMBER TRACKER ===\\n\\n";
  rows.forEach(r=>{
    const lbl = r.querySelector('.row-lbl');
    const val = r.querySelector('.row-val');
    if(lbl && val){
      const l = lbl.innerText.replace(/^[^a-zA-Z]+/,'').trim();
      const v = val.innerText.trim();
      text += l + ": " + v + "\\n";
    }
  });
  text += "\\n=====================================";
  navigator.clipboard.writeText(text).then(()=>{
    const btn = document.getElementById('copyBtn');
    btn.textContent = "✅ COPIED!";
    btn.classList.add('copied');
    showToast();
    setTimeout(()=>{ btn.textContent="📋 COPY ALL"; btn.classList.remove('copied'); },2500);
  }).catch(()=>{
    // fallback
    const ta = document.createElement('textarea');
    ta.value=text; document.body.appendChild(ta);
    ta.select(); document.execCommand('copy');
    document.body.removeChild(ta);
    showToast();
  });
}

function showToast(){
  const t=document.getElementById('toast');
  t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),2200);
}

// ── MAP ──────────────────────────────────────────────
{% if data %}
const mapEl = document.getElementById('map');
if(mapEl){
  const map = L.map('map').setView([20.59,78.96],5);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:''}).addTo(map);
  const addr = document.getElementById('addrVal')?.innerText;
  if(addr && addr !== 'N/A'){
    navigator.geolocation.getCurrentPosition(pos=>{
      const uLat=pos.coords.latitude, uLng=pos.coords.longitude;
      const youIcon=L.divIcon({html:'<div style="font-size:20px">📍</div>',className:''});
      L.marker([uLat,uLng],{icon:youIcon}).addTo(map).bindPopup('<b>YOU</b>');
      fetch('https://nominatim.openstreetmap.org/search?format=json&q='+encodeURIComponent(addr))
      .then(r=>r.json()).then(d=>{
        if(d.length>0){
          const tLat=parseFloat(d[0].lat), tLng=parseFloat(d[0].lon);
          const tgtIcon=L.divIcon({html:'<div style="font-size:20px">☠</div>',className:''});
          L.marker([tLat,tLng],{icon:tgtIcon}).addTo(map).bindPopup('<b>TARGET</b>');
          L.polyline([[uLat,uLng],[tLat,tLng]],{color:'#00ff41',weight:2,dashArray:'6 6'}).addTo(map);
          map.fitBounds([[uLat,uLng],[tLat,tLng]],{padding:[30,30]});
          const R=6371,dLat=(tLat-uLat)*Math.PI/180,dLon=(tLng-uLng)*Math.PI/180;
          const a=Math.sin(dLat/2)**2+Math.cos(uLat*Math.PI/180)*Math.cos(tLat*Math.PI/180)*Math.sin(dLon/2)**2;
          const km=(R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a))).toFixed(1);
          document.getElementById('dist-lbl').innerHTML='📏 Distance from you: <b>'+km+' KM</b>';
        }
      });
    }, ()=>{
      // no geolocation - just show target
      fetch('https://nominatim.openstreetmap.org/search?format=json&q='+encodeURIComponent(addr))
      .then(r=>r.json()).then(d=>{
        if(d.length>0){
          const tLat=parseFloat(d[0].lat), tLng=parseFloat(d[0].lon);
          map.setView([tLat,tLng],10);
          L.marker([tLat,tLng]).addTo(map).bindPopup('<b>TARGET LOCATION</b>').openPopup();
        }
      });
    });
  }
}
{% endif %}
</script>

</body>
</html>
"""

# ===== API =====
def fetch_data(number):
    try:
        url = f"https://exploitsindia.site/track/live.php?term={number}"
        res = requests.get(url, timeout=15)
        text = res.content.decode("utf-8", errors="replace")

        def get(pattern):
            m = re.search(pattern, text, re.IGNORECASE)
            return m.group(1).strip() if m else "N/A"

        return {
            "name":    get(r"Name:\s*(.+)"),
            "fname":   get(r"Father\s*Name:\s*(.+)"),
            "mobile":  get(r"Mobile:\s*(.+)") or number,
            "alt":     get(r"Alternate:\s*(.+)"),
            "circle":  get(r"Circle:\s*(.+)"),
            "email":   get(r"Email:\s*(.+)"),
            "address": get(r"Address:\s*(.+)"),
            "aadhaar": get(r"Aadhaar:\s*(.+)"),
        }

    except:
        return None

@app.route("/", methods=["GET","POST"])
def home():
    data = None
    if request.method == "POST":
        number = request.form.get("number")
        data = fetch_data(number)
    return render_template_string(HTML, data=data)

if __name__ == "__main__":
    try:
        from colorama import init, Fore, Style
        init()
        G  = Fore.GREEN
        B  = Style.BRIGHT
        D  = Style.DIM
        R  = Style.RESET_ALL
    except ImportError:
        G = B = D = R = ""

    banner = f"""
{G}{B}
  ███████╗██╗  ██╗██╗██╗   ██╗ █████╗ ███╗   ███╗
  ██╔════╝██║  ██║██║██║   ██║██╔══██╗████╗ ████║
  ███████╗███████║██║██║   ██║███████║██╔████╔██║
  ╚════██║██╔══██║██║╚██╗ ██╔╝██╔══██║██║╚██╔╝██║
  ███████║██║  ██║██║ ╚████╔╝ ██║  ██║██║ ╚═╝ ██║
  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝     ╚═╝
           H  A  C  K  E  R
{R}
{G}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}
{G}{B}      ⚡  BY  S H I V A M  H A C K E R  ⚡      {R}
{G}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}
{G}{D}  [*] Initializing modules...
  [*] Connecting to database...
  [*] Bypassing firewall...{R}
{G}{B}  [+] SERVER LIVE → http://127.0.0.1:5000{R}
{G}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}
"""
    print(banner)
    app.run(host="0.0.0.0", port=5000)