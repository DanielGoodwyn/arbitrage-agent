"""
Robinhood API Wrapper — Read-only access to real-time crypto quotes and portfolio data.
Uses official Robinhood Crypto API Keys (Base64) for authentication and data fetching.
"""
import logging
import base64
import time
import httpx
import uuid
import json
from typing import Optional, List
from datetime import datetime

from app.integrations.base import BaseIntegration
from app.agent.models import MarketData, AssetType

logger = logging.getLogger(__name__)


class RobinhoodClient(BaseIntegration):
    """
    Read-only Robinhood Official Crypto API client for:
    - Real-time crypto quotes
    - Portfolio positions

    Uses standard API requests authenticated via pynacl (Ed25519) signatures.
    """

    def __init__(self, api_key: str = "", private_key: str = ""):
        super().__init__("robinhood")
        self.api_key = api_key
        self.private_key_base64 = private_key
        self.base_url = "https://trading.robinhood.com"
        self._authenticated = False
        self.client = httpx.AsyncClient(base_url=self.base_url)
        self.signer = None

    async def initialize(self) -> bool:
        """Authenticate with Robinhood. Returns True if successful."""
        if not self.api_key or not self.private_key_base64:
            self.logger.warning("No official Robinhood API keys provided — running in mock mode")
            self._initialized = True
            return True

        try:
            import nacl.signing
            private_key_seed = base64.b64decode(self.private_key_base64)
            self.signer = nacl.signing.SigningKey(private_key_seed)
            self._authenticated = True
            self.logger.info("✅ Robinhood official API keys configured")
        except ImportError:
            self.logger.warning("pynacl not installed — running in mock mode")
            self._authenticated = False
        except Exception as e:
            self.logger.error(f"Robinhood auth failed: {e}")
            self._authenticated = False
            
        self._initialized = True
        return True

    async def update_credentials(self, api_key: str, private_key: str) -> bool:
        """Update credentials and re-authenticate on the fly."""
        self.api_key = api_key
        self.private_key_base64 = private_key
        self._authenticated = False
        return await self.initialize()

    def _get_headers(self, method: str, path: str, body: str = "") -> dict:
        timestamp = str(int(time.time()))
        message = f"{self.api_key}{timestamp}{path}{method}{body}"
        signed = self.signer.sign(message.encode("utf-8"))
        signature = base64.b64encode(signed.signature).decode("utf-8")
        return {
            "x-api-key": self.api_key,
            "x-signature": signature,
            "x-timestamp": timestamp,
            "Content-Type": "application/json"
        }

    async def _make_request(self, method: str, path: str, json_body: dict = None):
        body_str = ""
        if json_body:
            body_str = json.dumps(json_body)
        headers = self._get_headers(method, path, body_str)
        req = self.client.build_request(method, self.base_url + path, headers=headers, content=body_str if body_str else None)
        resp = await self.client.send(req)
        resp.raise_for_status()
        return resp.json()

    async def health_check(self) -> dict:
        return {
            "name": self.name,
            "authenticated": self._authenticated,
            "mode": "live" if self._authenticated else "mock",
            "status": "healthy",
        }

    async def shutdown(self) -> None:
        try:
            await self.client.aclose()
        except Exception:
            pass

    async def get_crypto_quote(self, symbol: str) -> MarketData:
        """Get real-time crypto quote. Falls back to mock data."""
        if self._authenticated:
            try:
                # Need to convert BTC to BTC-USD for the official API
                rh_symbol = symbol
                if "-" not in symbol:
                    rh_symbol = f"{symbol}-USD"
                    
                path = f"/api/v2/crypto/marketdata/best_bid_ask/?symbol={rh_symbol}"
                data = await self._make_request("GET", path)
                
                if data and "results" in data and len(data["results"]) > 0:
                    quote = data["results"][0]
                    price = float(quote.get("price", 0))
                    bid = float(quote.get("bid_inclusive_of_fee", price))
                    ask = float(quote.get("ask_inclusive_of_fee", price))
                    return MarketData(
                        symbol=symbol,
                        asset_type=AssetType.CRYPTO,
                        price=price,
                        bid=bid,
                        ask=ask,
                        volume=None,
                        source="robinhood_live_official",
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
        """Stocks are not supported on Robinhood Crypto API, returns mock data."""
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
        """Get current portfolio holdings. Uses get_crypto_positions."""
        if self._authenticated:
            try:
                positions = await self.get_crypto_positions()
                total_equity = sum([p["quantity"] * p["cost_bases"] for p in positions]) # rough estimate
                return {
                    "equity": total_equity,
                    "cash": 0, # Crypto API doesn't give fiat cash directly without another endpoint
                    "positions": positions,
                    "source": "robinhood_live_official",
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
                path = "/api/v1/crypto/trading/holdings/"
                data = await self._make_request("GET", path)
                
                if data and "results" in data:
                    return [
                        {
                            "symbol": pos.get("asset_code", "UNKNOWN"),
                            "quantity": float(pos.get("total_quantity", 0)),
                            "cost_bases": float(pos.get("quantity_available_for_trading", 0)) # Using available as a proxy for mock
                        }
                        for pos in data["results"] if float(pos.get("total_quantity", 0)) > 0
                    ]
            except Exception as e:
                self.logger.error(f"Failed to fetch crypto positions: {e}")

        # Mock crypto positions
        return [
            {"symbol": "BTC", "quantity": 0.15, "cost_bases": 13_800.00},
            {"symbol": "ETH", "quantity": 2.5, "cost_bases": 8_000.00},
            {"symbol": "SOL", "quantity": 25.0, "cost_bases": 4_500.00},
        ]
