"""
Robinhood API Wrapper — Read-only access to real-time quotes and portfolio data.
Uses robin_stocks library for authentication and data fetching.
"""
import logging
from typing import Optional, List
from datetime import datetime

from app.integrations.base import BaseIntegration
from app.agent.models import MarketData, AssetType

logger = logging.getLogger(__name__)


class RobinhoodClient(BaseIntegration):
    """
    Read-only Robinhood API client for:
    - Real-time crypto/stock quotes
    - Portfolio positions
    - Account holdings

    Uses robin_stocks/robinhood under the hood.
    """

    def __init__(self, username: str = "", password: str = "",
                 mfa_code: Optional[str] = None, device_token: Optional[str] = None):
        super().__init__("robinhood")
        self.username = username
        self.password = password
        self.mfa_code = mfa_code
        self.device_token = device_token
        self._authenticated = False

    async def initialize(self) -> bool:
        """Authenticate with Robinhood. Returns True if successful."""
        try:
            import robin_stocks.robinhood as rh

            if not self.username or not self.password:
                self.logger.warning("No Robinhood credentials provided — running in mock mode")
                self._initialized = True
                return True

            login_kwargs = {
                "username": self.username,
                "password": self.password,
                "store_session": True,
            }
            if self.mfa_code:
                login_kwargs["mfa_code"] = self.mfa_code
            if self.device_token:
                login_kwargs["device_token"] = self.device_token

            rh.login(**login_kwargs)
            self._authenticated = True
            self._initialized = True
            self.logger.info("✅ Robinhood authenticated successfully")
            return True

        except ImportError:
            self.logger.warning("robin_stocks not installed — running in mock mode")
            self._initialized = True
            return True
        except Exception as e:
            self.logger.error(f"Robinhood auth failed: {e}")
            self._initialized = True  # Still allow mock mode
            return False

    async def health_check(self) -> dict:
        return {
            "name": self.name,
            "authenticated": self._authenticated,
            "mode": "live" if self._authenticated else "mock",
            "status": "healthy",
        }

    async def shutdown(self) -> None:
        try:
            if self._authenticated:
                import robin_stocks.robinhood as rh
                rh.logout()
                self.logger.info("Robinhood logged out")
        except Exception:
            pass

    async def get_crypto_quote(self, symbol: str) -> MarketData:
        """Get real-time crypto quote. Falls back to mock data."""
        if self._authenticated:
            try:
                import robin_stocks.robinhood as rh
                quote = rh.crypto.get_crypto_quote(symbol)
                return MarketData(
                    symbol=symbol,
                    asset_type=AssetType.CRYPTO,
                    price=float(quote.get("mark_price", 0)),
                    bid=float(quote.get("bid_price", 0)),
                    ask=float(quote.get("ask_price", 0)),
                    volume=float(quote.get("volume", 0)) if quote.get("volume") else None,
                    source="robinhood_live",
                )
            except Exception as e:
                self.logger.error(f"Failed to fetch crypto quote for {symbol}: {e}")

        # Mock data fallback
        mock_prices = {"BTC": 97250.00, "ETH": 3420.50, "DOGE": 0.245, "SOL": 195.30}
        return MarketData(
            symbol=symbol,
            asset_type=AssetType.CRYPTO,
            price=mock_prices.get(symbol.upper(), 100.0),
            bid=mock_prices.get(symbol.upper(), 100.0) * 0.999,
            ask=mock_prices.get(symbol.upper(), 100.0) * 1.001,
            source="mock",
        )

    async def get_stock_quote(self, symbol: str) -> MarketData:
        """Get real-time stock quote. Falls back to mock data."""
        if self._authenticated:
            try:
                import robin_stocks.robinhood as rh
                quotes = rh.stocks.get_stock_quote_by_symbol(symbol)
                return MarketData(
                    symbol=symbol,
                    asset_type=AssetType.STOCK,
                    price=float(quotes.get("last_trade_price", 0)),
                    bid=float(quotes.get("bid_price", 0)),
                    ask=float(quotes.get("ask_price", 0)),
                    volume=float(quotes.get("volume", 0)) if quotes.get("volume") else None,
                    source="robinhood_live",
                )
            except Exception as e:
                self.logger.error(f"Failed to fetch stock quote for {symbol}: {e}")

        # Mock data fallback
        mock_prices = {"AAPL": 245.80, "TSLA": 342.15, "NVDA": 875.60, "SPY": 520.30, "DJT": 32.50}
        return MarketData(
            symbol=symbol,
            asset_type=AssetType.STOCK,
            price=mock_prices.get(symbol.upper(), 150.0),
            bid=mock_prices.get(symbol.upper(), 150.0) * 0.999,
            ask=mock_prices.get(symbol.upper(), 150.0) * 1.001,
            source="mock",
        )

    async def get_portfolio(self) -> dict:
        """Get current portfolio holdings."""
        if self._authenticated:
            try:
                import robin_stocks.robinhood as rh
                profile = rh.profiles.load_account_profile()
                positions = rh.account.get_all_positions()
                return {
                    "equity": float(profile.get("equity", 0)),
                    "cash": float(profile.get("cash", 0)),
                    "positions": [
                        {
                            "symbol": pos.get("symbol", "UNKNOWN"),
                            "quantity": float(pos.get("quantity", 0)),
                            "average_buy_price": float(pos.get("average_buy_price", 0)),
                        }
                        for pos in positions if float(pos.get("quantity", 0)) > 0
                    ],
                    "source": "robinhood_live",
                }
            except Exception as e:
                self.logger.error(f"Failed to fetch portfolio: {e}")

        # Mock portfolio
        return {
            "equity": 25_430.50,
            "cash": 5_200.00,
            "positions": [
                {"symbol": "AAPL", "quantity": 10, "average_buy_price": 240.00},
                {"symbol": "NVDA", "quantity": 5, "average_buy_price": 850.00},
                {"symbol": "BTC", "quantity": 0.15, "average_buy_price": 92_000.00},
                {"symbol": "ETH", "quantity": 2.5, "average_buy_price": 3_200.00},
            ],
            "source": "mock",
        }

    async def get_crypto_positions(self) -> list:
        """Get crypto-specific positions."""
        if self._authenticated:
            try:
                import robin_stocks.robinhood as rh
                positions = rh.crypto.get_crypto_positions()
                return [
                    {
                        "symbol": pos.get("currency", {}).get("code", "UNKNOWN"),
                        "quantity": float(pos.get("quantity", 0)),
                        "cost_bases": float(pos.get("cost_bases", [{}])[0].get("direct_cost_basis", 0))
                        if pos.get("cost_bases") else 0,
                    }
                    for pos in positions if float(pos.get("quantity", 0)) > 0
                ]
            except Exception as e:
                self.logger.error(f"Failed to fetch crypto positions: {e}")

        # Mock crypto positions
        return [
            {"symbol": "BTC", "quantity": 0.15, "cost_bases": 13_800.00},
            {"symbol": "ETH", "quantity": 2.5, "cost_bases": 8_000.00},
            {"symbol": "SOL", "quantity": 25.0, "cost_bases": 4_500.00},
        ]
