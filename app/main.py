"""
FastAPI Application — Autonomous Global Event Arbitrage Agent
Main entry point with embedded dashboard UI and agent lifecycle management.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.agent.orchestrator import AgentOrchestrator
from app.api.routes import router, set_orchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-20s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

orchestrator = AgentOrchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Autonomous Global Event Arbitrage Agent...")
    await orchestrator.initialize()
    set_orchestrator(orchestrator)
    yield
    logger.info("🛑 Shutting down agent...")
    await orchestrator.stop()


app = FastAPI(
    title="Autonomous Global Event Arbitrage Agent",
    description="Self-improving autonomous agent for real-time market arbitrage",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the live dashboard."""
    return DASHBOARD_HTML


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Arbitrage Agent — Live Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0e17;--surface:#111827;--surface2:#1a2332;--border:#1e293b;--accent:#6366f1;--accent2:#818cf8;--green:#22c55e;--red:#ef4444;--yellow:#eab308;--cyan:#06b6d4;--text:#e2e8f0;--text2:#94a3b8;--text3:#64748b;--glow:0 0 20px rgba(99,102,241,0.3)}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden}
.grain{position:fixed;top:0;left:0;width:100%;height:100%;opacity:0.03;pointer-events:none;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.header{padding:1.5rem 2rem;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;backdrop-filter:blur(20px);position:sticky;top:0;z-index:100;background:rgba(10,14,23,0.85)}
.logo{display:flex;align-items:center;gap:12px}
.logo-icon{width:40px;height:40px;background:linear-gradient(135deg,var(--accent),var(--cyan));border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:var(--glow)}
.logo h1{font-size:1.2rem;font-weight:700;background:linear-gradient(135deg,#fff,var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.logo p{font-size:0.7rem;color:var(--text3);text-transform:uppercase;letter-spacing:2px}
.controls{display:flex;gap:8px}
.btn{padding:8px 20px;border-radius:10px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-family:'Inter',sans-serif;font-size:0.8rem;font-weight:600;cursor:pointer;transition:all .2s;display:flex;align-items:center;gap:6px}
.btn:hover{border-color:var(--accent);box-shadow:var(--glow)}
.btn-primary{background:linear-gradient(135deg,var(--accent),#4f46e5);border-color:var(--accent)}
.btn-danger{border-color:var(--red)}
.btn-danger:hover{background:rgba(239,68,68,0.15)}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:1.5rem 2rem}
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.25rem;transition:all .3s}
.card:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:var(--glow)}
.card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.card-title{font-size:0.75rem;text-transform:uppercase;letter-spacing:1.5px;color:var(--text3);font-weight:600}
.card-value{font-size:2rem;font-weight:800;font-family:'JetBrains Mono',monospace}
.card-sub{font-size:0.75rem;color:var(--text2);margin-top:4px}
.positive{color:var(--green)}
.negative{color:var(--red)}
.neutral{color:var(--yellow)}
.main{display:grid;grid-template-columns:2fr 1fr;gap:16px;padding:0 2rem 2rem}
.panel{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.25rem;overflow:hidden}
.panel-title{font-size:0.85rem;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.log-entry{padding:10px 14px;border-radius:10px;margin-bottom:6px;font-family:'JetBrains Mono',monospace;font-size:0.72rem;line-height:1.5;background:var(--surface2);border-left:3px solid var(--accent);transition:all .2s}
.log-entry:hover{background:rgba(99,102,241,0.08)}
.log-entry.trade{border-left-color:var(--green)}
.log-entry.alert{border-left-color:var(--red)}
.log-entry.info{border-left-color:var(--cyan)}
.integration-row{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(30,41,59,0.5)}
.integration-row:last-child{border-bottom:none}
.int-name{font-size:0.8rem;font-weight:500;display:flex;align-items:center;gap:8px}
.dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.dot.on{background:var(--green);box-shadow:0 0 8px var(--green)}
.dot.off{background:var(--text3)}
.tag{font-size:0.65rem;padding:3px 8px;border-radius:6px;background:rgba(99,102,241,0.15);color:var(--accent2);font-weight:600}
.opp-row{padding:12px;background:var(--surface2);border-radius:10px;margin-bottom:8px}
.opp-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.opp-asset{font-weight:700;font-size:0.85rem}
.opp-score{font-family:'JetBrains Mono',monospace;font-size:0.8rem;font-weight:700}
.score-bar{height:4px;background:var(--border);border-radius:2px;margin-top:6px;overflow:hidden}
.score-fill{height:100%;border-radius:2px;transition:width .5s ease}
.pulse{animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
@media(max-width:1024px){.grid{grid-template-columns:repeat(2,1fr)}.main{grid-template-columns:1fr}}
@media(max-width:640px){.grid{grid-template-columns:1fr}.header{flex-direction:column;gap:12px}}
</style>
</head>
<body>
<div class="grain"></div>
<header class="header">
 <div class="logo">
  <div class="logo-icon">⚡</div>
  <div><h1>Arbitrage Agent</h1><p>Autonomous Event Arbitrage</p></div>
 </div>
 <div class="controls">
  <button class="btn" onclick="triggerCycle()">▶ Run Cycle</button>
  <button class="btn btn-primary" id="startBtn" onclick="startAgent()">🚀 Start Agent</button>
  <button class="btn btn-danger" id="stopBtn" onclick="stopAgent()">⏹ Stop</button>
 </div>
</header>

<div class="grid">
 <div class="card"><div class="card-header"><span class="card-title">Agent Cycles</span><span class="tag pulse" id="statusTag">IDLE</span></div><div class="card-value" id="cycleCount">0</div><div class="card-sub">Total cycles executed</div></div>
 <div class="card"><div class="card-header"><span class="card-title">Total P&L</span></div><div class="card-value" id="totalPnl">$0.00</div><div class="card-sub">Simulated trading performance</div></div>
 <div class="card"><div class="card-header"><span class="card-title">Trades Executed</span></div><div class="card-value" id="tradesCount">0</div><div class="card-sub">Buy/sell actions taken</div></div>
 <div class="card"><div class="card-header"><span class="card-title">Opportunities</span></div><div class="card-value" id="oppsCount">0</div><div class="card-sub">Arbitrage signals detected</div></div>
</div>

<div class="main">
 <div class="panel">
  <div class="panel-title">📊 Live Activity Feed</div>
  <div id="activityLog">
   <div class="log-entry info">System initialized — waiting for first cycle...</div>
  </div>
 </div>
 <div>
  <div class="panel" style="margin-bottom:16px">
   <div class="panel-title">🔌 Integrations (11)</div>
   <div id="integrations"></div>
   <div style="margin-top:16px;padding:12px;background:var(--surface2);border-radius:10px;font-size:0.8rem;border:1px solid var(--border)">
     <div style="margin-bottom:8px;font-weight:600;color:var(--accent2);display:flex;align-items:center;gap:6px"><span>🔗</span> Connect Live Robinhood Crypto (Official API)</div>
     <input type="text" id="rhApiKey" placeholder="API Key (Base64)" style="width:100%;padding:8px;background:var(--surface);color:#fff;border:1px solid var(--border);border-radius:6px;margin-bottom:6px;font-family:'Inter',sans-serif">
     <input type="password" id="rhPrivateKey" placeholder="Private Key (Base64)" style="width:100%;padding:8px;background:var(--surface);color:#fff;border:1px solid var(--border);border-radius:6px;margin-bottom:8px;font-family:'Inter',sans-serif">
     <button class="btn btn-primary" style="width:100%;justify-content:center" onclick="connectRobinhood()">Connect Account</button>
     <div id="rhAuthResult" style="margin-top:8px;text-align:center;font-weight:600"></div>
   </div>
  </div>
  <div class="panel">
   <div class="panel-title">🎯 Top Opportunities</div>
   <div id="opportunities"><div class="opp-row" style="color:var(--text3);text-align:center;font-size:0.8rem">Run a cycle to detect opportunities</div></div>
  </div>
 </div>
</div>

<script>
const API = '/api';
let refreshInterval;

async function fetchJSON(url, opts = {}) {
  try { const r = await fetch(API + url, opts); return await r.json(); }
  catch(e) { console.error(e); return null; }
}

async function refreshDashboard() {
  const s = await fetchJSON('/status');
  if (!s || s.status === 'not_initialized') return;
  document.getElementById('cycleCount').textContent = s.cycle_count || 0;
  const pnl = s.total_pnl || 0;
  const pnlEl = document.getElementById('totalPnl');
  pnlEl.textContent = '$' + pnl.toFixed(2);
  pnlEl.className = 'card-value ' + (pnl >= 0 ? 'positive' : 'negative');
  document.getElementById('tradesCount').textContent = s.trades_executed || 0;
  document.getElementById('oppsCount').textContent = s.opportunities_detected || 0;
  const tag = document.getElementById('statusTag');
  tag.textContent = s.is_running ? 'RUNNING' : 'IDLE';
  tag.style.background = s.is_running ? 'rgba(34,197,94,0.2)' : 'rgba(99,102,241,0.15)';
  tag.style.color = s.is_running ? '#22c55e' : '#818cf8';

  if (s.active_opportunities && s.active_opportunities.length > 0) {
    document.getElementById('opportunities').innerHTML = s.active_opportunities.slice(0,5).map(o => `
      <div class="opp-row">
        <div class="opp-header">
          <span class="opp-asset">${o.buy_asset.split('/')[0]}</span>
          <span class="opp-score ${o.predicted_score >= 0.75 ? 'positive' : o.predicted_score >= 0.5 ? 'neutral' : 'negative'}">${(o.predicted_score * 100).toFixed(1)}%</span>
        </div>
        <div style="font-size:0.7rem;color:var(--text2)">Spread: ${o.spread_pct.toFixed(3)}% | Sentiment: ${o.sentiment_score.toFixed(2)}</div>
        <div class="score-bar"><div class="score-fill" style="width:${o.predicted_score*100}%;background:${o.predicted_score>=0.75?'var(--green)':o.predicted_score>=0.5?'var(--yellow)':'var(--red)'}"></div></div>
      </div>
    `).join('');
  }
}

async function refreshIntegrations() {
  const h = await fetchJSON('/integrations');
  if (!h) return;
  document.getElementById('integrations').innerHTML = Object.entries(h).map(([k,v]) => `
    <div class="integration-row">
      <span class="int-name"><span class="dot ${v.status==='healthy'||v.status==='ok'?'on':'off'}"></span>${k}</span>
      <span class="tag">${v.mode || v.status || 'unknown'}</span>
    </div>
  `).join('');
}

function addLog(msg, type = 'info') {
  const log = document.getElementById('activityLog');
  const t = new Date().toLocaleTimeString();
  log.insertAdjacentHTML('afterbegin', `<div class="log-entry ${type}"><span style="color:var(--text3)">[${t}]</span> ${msg}</div>`);
  while (log.children.length > 30) log.lastChild.remove();
}

async function connectRobinhood() {
  const ak = document.getElementById('rhApiKey').value;
  const pk = document.getElementById('rhPrivateKey').value;
  if (!ak || !pk) {
    document.getElementById('rhAuthResult').textContent = "Please enter API Key and Private Key";
    document.getElementById('rhAuthResult').style.color = "var(--yellow)";
    return;
  }
  document.getElementById('rhAuthResult').textContent = "Authenticating...";
  document.getElementById('rhAuthResult').style.color = "var(--text3)";
  const r = await fetch(API + '/integrations/robinhood/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({api_key: ak, private_key: pk})
  });
  if (r.ok) {
    document.getElementById('rhAuthResult').textContent = "✅ Connected Live!";
    document.getElementById('rhAuthResult').style.color = "var(--green)";
    addLog('✅ Robinhood connected with live production data (Official API Key)', 'info');
    refreshIntegrations();
  } else {
    document.getElementById('rhAuthResult').textContent = "❌ Auth Failed (Check Keys)";
    document.getElementById('rhAuthResult').style.color = "var(--red)";
    addLog('❌ Robinhood API Key authentication failed', 'alert');
  }
}

async function triggerCycle() {
  addLog('⏳ Triggering manual cycle...', 'info');
  const r = await fetchJSON('/agent/cycle', {method:'POST'});
  if (r) {
    const steps = r.steps || {};
    if (steps.ingest) addLog(`📥 Ingested ${steps.ingest.crypto_quotes||0} crypto + ${steps.ingest.stock_quotes||0} stock quotes | Sentiment: ${(steps.ingest.sentiment_score||0).toFixed(2)}`, 'info');
    if (steps.analyze) addLog(`🔍 Found ${steps.analyze.patterns_detected||0} patterns, ${steps.analyze.correlations_found||0} correlations`, 'info');
    if (steps.predict) addLog(`🧠 ${steps.predict.opportunities_found||0} opportunities | Top score: ${(steps.predict.top_score||0).toFixed(4)} → ${steps.predict.decision?.action||'skip'}`, 'info');
    if (steps.execute?.traded) addLog(`💰 TRADE: ${steps.execute.trade.action} ${steps.execute.trade.quantity} ${steps.execute.trade.asset} @ $${steps.execute.trade.price.toLocaleString()}`, 'trade');
    if (steps.learn) addLog(`📈 P&L updated → Total: $${(steps.learn.total_pnl||0).toFixed(2)}`, steps.learn.total_pnl>=0?'trade':'alert');
    addLog(`✅ Cycle #${r.cycle} complete in ${(r.duration_seconds||0).toFixed(1)}s`, 'info');
  } else { addLog('❌ Cycle failed', 'alert'); }
  await refreshDashboard();
}

async function startAgent() {
  await fetchJSON('/agent/start', {method:'POST'});
  addLog('🚀 Agent loop STARTED — running autonomously', 'trade');
  refreshInterval = setInterval(refreshDashboard, 3000);
  await refreshDashboard();
}

async function stopAgent() {
  await fetchJSON('/agent/stop', {method:'POST'});
  addLog('⏹ Agent loop STOPPED', 'alert');
  if (refreshInterval) clearInterval(refreshInterval);
  await refreshDashboard();
}

// Initial load
refreshDashboard();
refreshIntegrations();
setInterval(refreshDashboard, 5000);
setInterval(refreshIntegrations, 15000);
</script>
</body>
</html>"""
