# 🚀 Autonomous Global Event Arbitrage Agent

A self-improving, autonomous agent that ingests real-time data, identifies complex market arbitrage opportunities (stocks & crypto), and acts on them.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATOR                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────┐  ┌────┐ │
│  │ INGEST  │→ │ ANALYZE │→ │ PREDICT │→ │EXECUTE│→ │LEARN│ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └───┬───┘  └──┬─┘ │
└───────┼────────────┼────────────┼────────────┼─────────┼───┘
        │            │            │            │         │
   ┌────▼────┐  ┌────▼────┐  ┌───▼────┐  ┌───▼───┐ ┌───▼───┐
   │Robinhood│  │  Reka   │  │Fastino │  │Modulate│ │Numeric│
   │ Airbyte │  │  Neo4j  │  │ Senso  │  │  R.H.  │ │ Neo4j │
   │ Tavily  │  │ Yutori  │  │        │  │        │ │       │
   └─────────┘  └─────────┘  └────────┘  └───────┘ └───────┘
```

## 10 Sponsor Integrations

👉 **[View the detailed Sponsor Integration matrix and API usage here](https://danielgoodwyn.com/arbitrage/sponsors/)**

| Sponsor | Role | Status |
|---------|------|--------|
| **Senso** | Context OS / agent state | ✅ Mock ready |
| **Airbyte** | Data ingestion streams | ✅ Mock ready |
| **Tavily** | Web search & sentiment | ✅ Mock ready |
| **Reka** | Vision API / chart analysis | ✅ Mock ready |
| **Neo4j** | Knowledge graph & memory | ✅ Mock ready |
| **Fastino Labs** | Prediction model | ✅ Mock ready |
| **Yutori** | N1 Navigator / routing | ✅ Mock ready |
| **Numeric** | Accounting & P&L | ✅ Mock ready |
| **Modulate** | Voice emergency alerts | ✅ Mock ready |
| **Render** | Deployment (2+ services) | ✅ Configured |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy env template
cp .env.example .env

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open **http://localhost:8000** for the live dashboard.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Live dashboard UI |
| GET | `/api/health` | Health check |
| GET | `/api/status` | Agent state |
| GET | `/api/portfolio` | Portfolio snapshot |
| GET | `/api/quotes/{type}/{symbol}` | Real-time quote |
| POST | `/api/agent/start` | Start autonomous loop |
| POST | `/api/agent/stop` | Stop autonomous loop |
| POST | `/api/agent/cycle` | Trigger single cycle |
| GET | `/api/integrations` | Integration health |
| GET | `/api/pnl` | P&L summary |
| GET | `/api/graph/stats` | Neo4j stats |
| GET | `/api/model/status` | Fastino model status |
| GET | `/api/alerts` | Voice alert history |

## Deploy to Render

1. Push to GitHub
2. Connect repo on [Render Dashboard](https://dashboard.render.com)
3. Use `render.yaml` Blueprint for auto-config
4. Set environment variables in Render dashboard

## License

MIT — Built for SF Agents Hackathon 2026
