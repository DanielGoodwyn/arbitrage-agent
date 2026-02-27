"""
Core data models for the Arbitrage Agent.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AssetType(str, Enum):
    STOCK = "stock"
    CRYPTO = "crypto"


class MarketData(BaseModel):
    """Real-time market data for a single asset."""
    symbol: str
    asset_type: AssetType
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "robinhood"


class SentimentData(BaseModel):
    """Sentiment analysis from news/web sources."""
    query: str
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    sources: List[str] = []
    summary: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VisualPattern(BaseModel):
    """Pattern detected from chart/image analysis."""
    pattern_type: str
    asset_symbol: str
    confidence: float = Field(ge=0.0, le=1.0)
    description: str = ""
    image_url: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ArbitrageOpportunity(BaseModel):
    """A detected arbitrage opportunity."""
    id: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y%m%d%H%M%S"))
    buy_asset: str
    sell_asset: str
    buy_price: float
    sell_price: float
    spread_pct: float
    predicted_score: float = Field(ge=0.0, le=1.0, default=0.0)
    sentiment_score: float = Field(ge=-1.0, le=1.0, default=0.0)
    visual_patterns: List[VisualPattern] = []
    neo4j_correlations: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "detected"

    @property
    def is_actionable(self) -> bool:
        return self.predicted_score >= 0.75

    @property
    def is_anomaly(self) -> bool:
        return self.predicted_score >= 0.95 or abs(self.spread_pct) > 5.0


class TradeAction(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class TradeResult(BaseModel):
    """Result of a simulated or real trade execution."""
    opportunity_id: str
    action: TradeAction
    asset: str
    quantity: float
    price: float
    simulated: bool = True
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    order_id: Optional[str] = None
    notes: str = ""


class PnLRecord(BaseModel):
    """Profit & Loss record for a completed trade cycle."""
    trade_id: str
    opportunity_id: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_pct: float
    asset: str
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    feedback_sent: bool = False


class AgentState(BaseModel):
    """Current state of the autonomous agent."""
    cycle_count: int = 0
    last_cycle_at: Optional[datetime] = None
    opportunities_detected: int = 0
    trades_executed: int = 0
    total_pnl: float = 0.0
    is_running: bool = False
    active_opportunities: List[ArbitrageOpportunity] = []
    recent_trades: List[TradeResult] = []
    errors: List[str] = []
    integration_status: dict = {}
