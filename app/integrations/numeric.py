"""
Numeric — Structured accounting and P&L tracking.
Simulates clean trade accounting that feeds the agent's self-improvement loop.
"""
from app.integrations.base import BaseIntegration
from app.agent.models import TradeResult, PnLRecord
from typing import List, Dict, Any
from datetime import datetime


class NumericClient(BaseIntegration):
    """
    Numeric integration for trade accounting and P&L.
    Phase 1: Mock implementation with in-memory ledger.
    """

    def __init__(self, api_key: str = "", base_url: str = "https://api.numeric.io"):
        super().__init__("numeric")
        self.api_key = api_key
        self.base_url = base_url
        self._ledger: List[Dict[str, Any]] = []
        self._total_pnl: float = 0.0

    async def initialize(self) -> bool:
        self._initialized = True
        self.logger.info("✅ Numeric initialized (mock mode)")
        return True

    async def health_check(self) -> dict:
        return {"name": self.name, "status": "healthy", "mode": "mock",
                "total_entries": len(self._ledger), "total_pnl": self._total_pnl}

    async def shutdown(self) -> None:
        pass

    async def log_trade(self, trade: TradeResult) -> dict:
        """Log a trade execution to the accounting ledger."""
        entry = {
            "id": f"ledger-{len(self._ledger) + 1}",
            "opportunity_id": trade.opportunity_id,
            "action": trade.action.value,
            "asset": trade.asset,
            "quantity": trade.quantity,
            "price": trade.price,
            "total_value": trade.quantity * trade.price,
            "simulated": trade.simulated,
            "timestamp": trade.executed_at.isoformat(),
        }
        self._ledger.append(entry)
        return entry

    async def get_pnl(self, period: str = "all") -> Dict[str, Any]:
        """Get P&L summary for a given period."""
        return {
            "period": period,
            "total_pnl": self._total_pnl,
            "total_trades": len(self._ledger),
            "winning_trades": int(len(self._ledger) * 0.6),
            "losing_trades": int(len(self._ledger) * 0.4),
            "win_rate": 0.60,
            "best_trade": 450.25,
            "worst_trade": -180.50,
            "sharpe_ratio": 1.45,
        }

    async def record_pnl(self, record: PnLRecord) -> None:
        """Record a completed P&L entry."""
        self._total_pnl += record.pnl
        entry = {
            "type": "pnl",
            "trade_id": record.trade_id,
            "pnl": record.pnl,
            "pnl_pct": record.pnl_pct,
            "asset": record.asset,
            "timestamp": record.recorded_at.isoformat(),
        }
        self._ledger.append(entry)

    async def generate_report(self) -> Dict[str, Any]:
        """Generate a structured accounting report."""
        pnl = await self.get_pnl()
        return {
            "report_date": datetime.utcnow().isoformat(),
            "summary": pnl,
            "entries": self._ledger[-10:],  # Last 10 entries
            "total_entries": len(self._ledger),
        }
