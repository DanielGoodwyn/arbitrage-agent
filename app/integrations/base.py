"""
Abstract base class for all sponsor integrations.
Each integration must implement initialize, health_check, and shutdown.
"""
from abc import ABC, abstractmethod
from typing import Any
import logging

logger = logging.getLogger(__name__)


class BaseIntegration(ABC):
    """Base class for all service integrations."""

    def __init__(self, name: str):
        self.name = name
        self._initialized = False
        self.logger = logging.getLogger(f"integration.{name}")

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the integration. Returns True if successful."""
        ...

    @abstractmethod
    async def health_check(self) -> dict:
        """Check if the integration is healthy. Returns status dict."""
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        """Clean shutdown of the integration."""
        ...

    @property
    def is_ready(self) -> bool:
        return self._initialized

    def status(self) -> dict:
        return {
            "name": self.name,
            "initialized": self._initialized,
            "ready": self.is_ready,
        }
