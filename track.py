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

/* ── LOADER ── */
#loader {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(3,15,3,0.93);
  z-index: 99999;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 22px;
}

.loader-ring {
  width: 64px; height: 64px;
  border: 3px solid rgba(0,255,65,0.15);
  border-top: 3px solid var(--g);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  box-shadow: 0 0 18px var(--g);
}
@keyframes spin { to { transform: rotate(360deg); } }

.loader-text {
  font-family: 'Orbitron', sans-serif;
  font-size: 13px;
  color: var(--g);
  letter-spacing: 4px;
  text-shadow: 0 0 10px var(--g);
}
.loader-status {
  font-size: 11px;
  color: var(--gdim);
  letter-spacing: 3px;
  opacity: 0.7;
}

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
    <form method="POST" id="trackForm">
      <input type="text" name="number" placeholder="ENTER MOBILE NUMBER" required autocomplete="off" id="numInput">
      <button type="submit" class="btn-track" id="trackBtn" onclick="showLoader()">&#x26A1; TRACK NOW &#x26A1;</button>
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
      <span class="row-lbl">🪦 AADHAAR</span>
      <span class="row-val aadhaar-val">{{ data.aadhaar }}</span>
    </div>
    {% endif %}

    {% if data.address and data.address != 'N/A' %}
    <div style="margin-top:18px;">
      <div style="font-size:10px; letter-spacing:3px; color:rgba(0,255,65,0.5); margin-bottom:8px;">// GOOGLE MAP LOCATION</div>
      <iframe
        id="gmap"
        src="https://maps.google.com/maps?q={{ data.address | urlencode }}&output=embed&z=14"
        width="100%%"
        height="280"
        style="border:1px solid rgba(0,255,65,0.3); border-radius:8px; display:block; box-shadow:0 0 18px rgba(0,255,65,0.08);"
        allowfullscreen
        loading="lazy"
        referrerpolicy="no-referrer-when-downgrade">
      </iframe>
      <a href="https://www.google.com/maps/search/?api=1&query={{ data.address | urlencode }}"
         target="_blank"
         style="display:inline-block; margin-top:10px; padding:9px 20px; background:rgba(0,255,65,0.08); border:1px solid rgba(0,255,65,0.4); border-radius:6px; color:var(--g); font-family:'JetBrains Mono',monospace; font-size:11px; letter-spacing:2px; text-decoration:none;">
        &#x1F30D; FULL GOOGLE MAPS M DEKHO
      </a>
    </div>
    {% endif %}

  </div>
  {% endif %}

  <!-- NOT FOUND CARD -->
  {% if searched and not data %}
  <div class="card" style="text-align:center; padding:40px 24px;">
    <div style="font-size:52px; margin-bottom:16px; animation:blink 1.5s infinite;">&#x1F914;</div>
    <div style="font-family:'Orbitron',sans-serif; font-size:18px; color:#ffaa00; letter-spacing:3px; text-shadow:0 0 12px #ffaa00; margin-bottom:16px;">MAAF KIJIYE</div>
    <div style="border-top:1px solid rgba(0,255,65,0.15); padding-top:16px; font-size:13px; color:rgba(200,255,212,0.65); letter-spacing:2px; line-height:2.2;">
      <span style="color:#ffaa00;">&#x26A0;</span> Is number ki koi jankari<br>
      hamare server mein available nahi hai.<br><br>
      <span style="font-size:11px; color:rgba(0,255,65,0.4);">[ Number registered nahi hai ya data nahi mila ]</span>
    </div>
    <div style="margin-top:20px;">
      <button onclick="window.location.href='/'" style="padding:10px 28px; background:rgba(255,170,0,0.12); border:1px solid #ffaa00; border-radius:6px; color:#ffaa00; font-family:'JetBrains Mono',monospace; font-size:12px; letter-spacing:3px; cursor:pointer;">&#x21BA; DOBARA TRY KARO</button>
    </div>
  </div>
  {% endif %}

</div>

<!-- FOOTER -->
<div class="ftr">CODED BY <span>SHIVAM HACKER</span> &nbsp;|&nbsp; ALL RIGHTS RESERVED &nbsp;|&nbsp; <span>☠</span></div>

</div><!-- /wrap -->

<!-- LOADER OVERLAY (outside wrap) -->
<div id="loader">
  <div class="loader-ring"></div>
  <div class="loader-text">TRACKING TARGET<span id="ldots">...</span></div>
  <div class="loader-status" id="loaderStatus">[*] CONNECTING TO DATABASE...</div>
</div>

<!-- TOAST -->
<div class="toast" id="toast">✅ DATA COPIED!</div>

<script>
// ── VOICE (Web Speech API) ───────────────────────────
function speak(text, lang){
  if(!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(text);
  u.lang = lang || 'hi-IN';
  u.rate = 0.92;
  u.pitch = 1;
  window.speechSynthesis.speak(u);
}

// Auto-speak on page load based on result
window.addEventListener('load', function(){
  {% if data and data.name != 'N/A' %}
    speak('Target ki jankari mil gayi. Data screen par show ho raha hai.');
  {% elif searched %}
    speak('Khed hai. Hamare server mein is number ka koi data nahi mila.');
  {% endif %}
});

// ── LOADER ───────────────────────────────────────────
var loaderMsgs = [
  '[*] CONNECTING TO DATABASE...',
  '[*] BYPASSING FIREWALL...',
  '[*] LOCATING TARGET...',
  '[*] EXTRACTING RECORDS...',
  '[*] DECRYPTING DATA...'
];
function showLoader(){
  var numVal = document.getElementById('numInput').value.trim();
  if(!numVal) return;
  // Voice: bolo ki search shuru ho raha hai (number mat bolo)
  speak('Number ki jankari nikali ja rahi hai. Kripya prateeksha karein.');
  document.getElementById('loader').style.display = 'flex';
  var si = 0;
  var dotStr = ['.','..','...'];
  var di = 0;
  setInterval(function(){
    document.getElementById('loaderStatus').textContent = loaderMsgs[si % loaderMsgs.length];
    si++;
  }, 900);
  setInterval(function(){
    document.getElementById('ldots').textContent = dotStr[di % 3];
    di++;
  }, 400);
}

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

// ── Google Maps iframe loaded via HTML (no JS needed) ─
</script>

</body>
</html>
"""

# ===== API ===== (2 retries)
import time

def fetch_data(number):
    url = f"https://exploitsindia.site/track/live.php?term={number}"

    for attempt in range(2):          # try 2 times
        try:
            res = requests.get(url, timeout=15)
            text = res.content.decode("utf-8", errors="replace")

            def get(pattern):
                m = re.search(pattern, text, re.IGNORECASE)
                return m.group(1).strip() if m else "N/A"

            name = get(r"Name:\s*(.+)")

            # Agar name N/A hai aur pehla attempt hai → retry
            if name == "N/A" and attempt == 0:
                time.sleep(1)
                continue

            # Dono try ke baad bhi N/A → data nahi mila
            if name == "N/A":
                return None

            return {
                "name":    name,
                "fname":   get(r"Father\s*Name:\s*(.+)"),
                "mobile":  get(r"Mobile:\s*(.+)") or number,
                "alt":     get(r"Alternate:\s*(.+)"),
                "circle":  get(r"Circle:\s*(.+)"),
                "email":   get(r"Email:\s*(.+)"),
                "address": get(r"Address:\s*(.+)"),
                "aadhaar": get(r"Aadhaar:\s*(.+)"),
            }
        except Exception:
            if attempt == 0:
                time.sleep(1)   # 1 second wait then retry
            else:
                return None
    return None

@app.route("/", methods=["GET","POST"])
def home():
    data = None
    searched = False
    if request.method == "POST":
        number = request.form.get("number", "").strip()
        searched = True
        if number:
            data = fetch_data(number)
    return render_template_string(HTML, data=data, searched=searched)

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