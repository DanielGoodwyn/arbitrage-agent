"""
Core Agent Orchestrator — The autonomous loop that runs the 5-step workflow:
1. INGEST  — Pull data from Robinhood, Airbyte, Tavily
2. ANALYZE — Route through Yutori → Reka → Neo4j for correlations
3. PREDICT — Fastino scores the opportunity (Senso manages context)
4. EXECUTE — Simulate/execute trade via Robinhood + optional Modulate voice alert
5. LEARN   — Numeric logs P&L → updates Neo4j for future predictions
"""
import asyncio
import logging
import random
from datetime import datetime
from typing import Optional

from app.config import settings
from app.agent.models import (
    AgentState, ArbitrageOpportunity, TradeResult, TradeAction, PnLRecord
)
from app.integrations.robinhood import RobinhoodClient
from app.integrations.senso import SensoClient
from app.integrations.airbyte import AirbyteClient
from app.integrations.tavily import TavilyClient
from app.integrations.reka import RekaClient
from app.integrations.neo4j_client import Neo4jClient
from app.integrations.fastino import FastinoClient
from app.integrations.yutori import YutoriClient
from app.integrations.numeric import NumericClient
from app.integrations.modulate import ModulateClient

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    The Autonomous Global Event Arbitrage Agent.
    Continuously ingests data, detects opportunities, and executes trades.
    """

    def __init__(self):
        self.state = AgentState()
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._cycle_logs: list = []

        # Initialize all integrations
        self.robinhood = RobinhoodClient(
            api_key=settings.robinhood_api_key,
            private_key=settings.robinhood_private_key,
        )
        self.senso = SensoClient(api_key=settings.senso_api_key, base_url=settings.senso_base_url)
        self.airbyte = AirbyteClient(
            api_key=settings.airbyte_api_key, base_url=settings.airbyte_base_url,
            workspace_id=settings.airbyte_workspace_id,
        )
        self.tavily = TavilyClient(api_key=settings.tavily_api_key)
        self.reka = RekaClient(api_key=settings.reka_api_key, base_url=settings.reka_base_url)
        self.neo4j = Neo4jClient(
            uri=settings.neo4j_uri, username=settings.neo4j_username, password=settings.neo4j_password,
        )
        self.fastino = FastinoClient(api_key=settings.fastino_api_key, base_url=settings.fastino_base_url)
        self.yutori = YutoriClient(api_key=settings.yutori_api_key, base_url=settings.yutori_base_url)
        self.numeric = NumericClient(api_key=settings.numeric_api_key, base_url=settings.numeric_base_url)
        self.modulate = ModulateClient(api_key=settings.modulate_api_key, base_url=settings.modulate_base_url)

        self._integrations = [
            self.robinhood, self.senso, self.airbyte, self.tavily, self.reka,
            self.neo4j, self.fastino, self.yutori, self.numeric, self.modulate,
        ]

        # Watchlist
        self.crypto_watchlist = ["BTC", "ETH", "SOL", "DOGE"]
        self.stock_watchlist = ["AAPL", "TSLA", "NVDA", "SPY", "DJT"]

    async def initialize(self) -> dict:
        """Initialize all integrations and return status."""
        logger.info("🚀 Initializing Autonomous Arbitrage Agent...")
        results = {}
        for integration in self._integrations:
            try:
                success = await integration.initialize()
                results[integration.name] = {"status": "ok" if success else "degraded", "ready": integration.is_ready}
                logger.info(f"  {'✅' if success else '⚠️'} {integration.name}")
            except Exception as e:
                results[integration.name] = {"status": "error", "error": str(e)}
                logger.error(f"  ❌ {integration.name}: {e}")

        self.state.integration_status = results
        await self.senso.update_context("integrations", results)
        logger.info("🤖 Agent initialization complete")
        return results

    async def start(self) -> None:
        """Start the autonomous agent loop."""
        if self._running:
            logger.warning("Agent is already running")
            return
        self._running = True
        self.state.is_running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("▶️ Agent loop started")

    async def stop(self) -> None:
        """Stop the autonomous agent loop."""
        self._running = False
        self.state.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("⏹️ Agent loop stopped")

    async def _run_loop(self) -> None:
        """Main autonomous loop."""
        while self._running:
            try:
                await self._run_cycle()
                await asyncio.sleep(settings.agent_cycle_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cycle error: {e}")
                self.state.errors.append(f"{datetime.utcnow().isoformat()}: {e}")
                await asyncio.sleep(5)

    async def _run_cycle(self) -> dict:
        """Execute one full agent cycle (Ingest → Analyze → Predict → Execute → Learn)."""
        cycle_start = datetime.utcnow()
        self.state.cycle_count += 1
        cycle_id = self.state.cycle_count
        log = {"cycle": cycle_id, "started_at": cycle_start.isoformat(), "steps": {}}

        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 CYCLE #{cycle_id} starting at {cycle_start.isoformat()}")
        logger.info(f"{'='*60}")

        await self.senso.set_workflow_state("ingesting")

        # ── STEP 1: INGEST ──────────────────────────────────
        logger.info("📥 Step 1: INGEST — Fetching market data...")
        nav_plan = await self.yutori.get_navigation_plan("ingest")

        # Fetch crypto quotes
        crypto_data = {}
        for symbol in self.crypto_watchlist:
            crypto_data[symbol] = await self.robinhood.get_crypto_quote(symbol)

        # Fetch stock quotes
        stock_data = {}
        for symbol in self.stock_watchlist:
            stock_data[symbol] = await self.robinhood.get_stock_quote(symbol)

        # Fetch economic indicators
        economic_data = await self.airbyte.get_latest_records("economic_indicators")

        # Fetch sentiment
        sentiment = await self.tavily.get_sentiment("crypto market momentum")
        trending = await self.tavily.get_trending_news("crypto")

        portfolio = await self.robinhood.get_portfolio()

        log["steps"]["ingest"] = {
            "crypto_quotes": len(crypto_data),
            "stock_quotes": len(stock_data),
            "economic_indicators": len(economic_data),
            "sentiment_score": sentiment.sentiment_score,
        }
        logger.info(f"  📊 {len(crypto_data)} crypto, {len(stock_data)} stock quotes fetched")
        logger.info(f"  📰 Sentiment: {sentiment.sentiment_score:.2f} | {len(trending)} trending news")

        # ── STEP 2: ANALYZE ─────────────────────────────────
        await self.senso.set_workflow_state("analyzing")
        logger.info("🔍 Step 2: ANALYZE — Finding patterns & correlations...")

        # Analyze charts with Reka Vision
        chart_patterns = []
        for symbol in self.crypto_watchlist[:2]:
            pattern = await self.reka.analyze_chart(symbol, "4h")
            chart_patterns.append(pattern)
            await self.yutori.route_data("visual_pattern", pattern.model_dump())

        # Find historical correlations in Neo4j
        correlations = await self.neo4j.find_correlations("market_move", self.crypto_watchlist[0])

        # Store events in knowledge graph
        for symbol, data in crypto_data.items():
            await self.neo4j.store_event("price_snapshot", data.model_dump())

        log["steps"]["analyze"] = {
            "patterns_detected": len(chart_patterns),
            "correlations_found": len(correlations),
        }
        logger.info(f"  🎯 {len(chart_patterns)} visual patterns, {len(correlations)} correlations")

        # ── STEP 3: PREDICT ─────────────────────────────────
        await self.senso.set_workflow_state("predicting")
        logger.info("🧠 Step 3: PREDICT — Scoring arbitrage opportunities...")

        opportunities = []
        # Detect cross-exchange spread opportunities (simulated)
        for symbol in self.crypto_watchlist:
            data = crypto_data[symbol]
            if data.bid and data.ask:
                spread_pct = ((data.ask - data.bid) / data.bid) * 100
                if spread_pct > 0.05:  # Any meaningful spread
                    opp_data = {
                        "spread_pct": spread_pct,
                        "sentiment_score": sentiment.sentiment_score,
                        "correlations": correlations,
                        "patterns": [p.model_dump() for p in chart_patterns],
                    }
                    score = await self.fastino.predict_opportunity(opp_data, await self.senso.get_context())

                    opp = ArbitrageOpportunity(
                        buy_asset=f"{symbol}/Exchange-A",
                        sell_asset=f"{symbol}/Exchange-B",
                        buy_price=data.bid,
                        sell_price=data.ask,
                        spread_pct=spread_pct,
                        predicted_score=score,
                        sentiment_score=sentiment.sentiment_score,
                        visual_patterns=chart_patterns,
                        neo4j_correlations=[c["event"] for c in correlations],
                    )
                    opportunities.append(opp)

        # Sort by score
        opportunities.sort(key=lambda o: o.predicted_score, reverse=True)

        # Route decision through Yutori
        decision = {"action": "skip", "urgency": "low", "reason": "No opportunities"}
        top_opp = None
        if opportunities:
            top_opp = opportunities[0]
            decision = await self.yutori.make_decision({"predicted_score": top_opp.predicted_score})

        await self.senso.update_context("last_opportunities", len(opportunities))
        await self.senso.update_context("top_score", top_opp.predicted_score if top_opp else 0)

        log["steps"]["predict"] = {
            "opportunities_found": len(opportunities),
            "top_score": top_opp.predicted_score if top_opp else 0,
            "decision": decision,
        }
        logger.info(f"  💡 {len(opportunities)} opportunities found")
        if top_opp:
            logger.info(f"  🏆 Top: {top_opp.buy_asset} | Score: {top_opp.predicted_score:.4f} | Decision: {decision['action']}")

        # ── STEP 4: EXECUTE ─────────────────────────────────
        await self.senso.set_workflow_state("executing")
        logger.info("⚡ Step 4: EXECUTE — Processing decisions...")

        trade = None
        if top_opp and decision["action"] in ("execute", "execute_and_alert"):
            trade = TradeResult(
                opportunity_id=top_opp.id,
                action=TradeAction.BUY,
                asset=top_opp.buy_asset.split("/")[0],
                quantity=round(random.uniform(0.01, 0.1), 4),
                price=top_opp.buy_price,
                simulated=True,
                notes=f"Score: {top_opp.predicted_score:.4f} | {decision['reason']}",
            )
            self.state.trades_executed += 1
            self.state.recent_trades = [trade] + self.state.recent_trades[:9]
            logger.info(f"  💰 SIMULATED TRADE: {trade.action.value} {trade.quantity} {trade.asset} @ ${trade.price:,.2f}")

            # Emergency voice alert for anomalies
            if decision["action"] == "execute_and_alert" or (top_opp and top_opp.is_anomaly):
                await self.modulate.send_alert(
                    f"ANOMALY DETECTED: {top_opp.buy_asset} spread {top_opp.spread_pct:.2f}% "
                    f"with score {top_opp.predicted_score:.4f}",
                    severity="critical",
                    opportunity_id=top_opp.id,
                )
                logger.warning("  🚨 Modulate voice alert triggered!")
        else:
            logger.info("  ⏭️ No trade executed this cycle")

        log["steps"]["execute"] = {
            "traded": trade is not None,
            "trade": trade.model_dump() if trade else None,
        }

        # ── STEP 5: LEARN ───────────────────────────────────
        await self.senso.set_workflow_state("learning")
        logger.info("📚 Step 5: LEARN — Updating knowledge base...")

        if trade:
            # Log to Numeric accounting
            await self.numeric.log_trade(trade)

            # Simulate P&L (mock — in production this would be real)
            mock_pnl = round(random.uniform(-50, 150), 2)
            pnl_record = PnLRecord(
                trade_id=trade.order_id or f"sim-{self.state.cycle_count}",
                opportunity_id=trade.opportunity_id,
                entry_price=trade.price,
                exit_price=trade.price * (1 + mock_pnl / (trade.price * trade.quantity)),
                quantity=trade.quantity,
                pnl=mock_pnl,
                pnl_pct=round((mock_pnl / (trade.price * trade.quantity)) * 100, 2),
                asset=trade.asset,
            )
            await self.numeric.record_pnl(pnl_record)
            self.state.total_pnl += mock_pnl

            # Update Neo4j with trade outcome
            await self.neo4j.update_trade_outcome(
                trade_id=pnl_record.trade_id,
                pnl=mock_pnl,
                success=mock_pnl > 0,
            )
            logger.info(f"  📈 P&L: ${mock_pnl:+.2f} | Total: ${self.state.total_pnl:+.2f}")

        log["steps"]["learn"] = {
            "pnl_updated": trade is not None,
            "total_pnl": self.state.total_pnl,
        }

        # ── CYCLE COMPLETE ──────────────────────────────────
        self.state.last_cycle_at = datetime.utcnow()
        self.state.opportunities_detected += len(opportunities)
        self.state.active_opportunities = opportunities[:5]
        await self.senso.set_workflow_state("idle")

        log["completed_at"] = datetime.utcnow().isoformat()
        log["duration_seconds"] = (datetime.utcnow() - cycle_start).total_seconds()
        self._cycle_logs.append(log)
        if len(self._cycle_logs) > 50:
            self._cycle_logs = self._cycle_logs[-50:]

        logger.info(f"✅ Cycle #{cycle_id} complete in {log['duration_seconds']:.1f}s")
        logger.info(f"   Total: {self.state.trades_executed} trades | ${self.state.total_pnl:+.2f} P&L")

        return log

    async def run_single_cycle(self) -> dict:
        """Run a single cycle on-demand (for API triggers)."""
        return await self._run_cycle()

    def get_state(self) -> dict:
        """Get current agent state as dict."""
        return {
            **self.state.model_dump(),
            "last_cycle_at": self.state.last_cycle_at.isoformat() if self.state.last_cycle_at else None,
            "recent_trades": [t.model_dump() for t in self.state.recent_trades],
            "active_opportunities": [o.model_dump() for o in self.state.active_opportunities],
        }

    def get_cycle_logs(self, limit: int = 10) -> list:
        """Get recent cycle logs."""
        return self._cycle_logs[-limit:]

    async def get_integration_health(self) -> dict:
        """Check health of all integrations."""
        health = {}
        for integration in self._integrations:
            try:
                health[integration.name] = await integration.health_check()
            except Exception as e:
                health[integration.name] = {"status": "error", "error": str(e)}
        return health
