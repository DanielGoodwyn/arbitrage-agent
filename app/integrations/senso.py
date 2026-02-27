"""
Senso (Context OS) — Agent state and context management.
Manages the agent's working memory, workflow state, and context persistence.
"""
from app.integrations.base import BaseIntegration
from typing import Any, Dict, Optional
from datetime import datetime


class SensoClient(BaseIntegration):
    """
    Senso Context OS integration for managing agent state.
    Phase 1: Mock implementation using in-memory state.
    """

    def __init__(self, api_key: str = "", base_url: str = "https://api.senso.ai"):
        super().__init__("senso")
        self.api_key = api_key
        self.base_url = base_url
        self._context: Dict[str, Any] = {}
        self._workflow_state: str = "idle"

    async def initialize(self) -> bool:
        self._context = {
            "agent_id": "arbitrage-agent-v1",
            "started_at": datetime.utcnow().isoformat(),
            "mode": "autonomous",
        }
        self._initialized = True
        self.logger.info("✅ Senso Context OS initialized (mock mode)")
        return True

    async def health_check(self) -> dict:
        return {"name": self.name, "status": "healthy", "mode": "live" if self.api_key else "mock", "context_keys": len(self._context)}

    async def shutdown(self) -> None:
        self._context.clear()

    async def get_context(self, key: Optional[str] = None) -> Any:
        """Get the current agent context or a specific key."""
        if key:
            return self._context.get(key)
        return self._context.copy()

    async def update_context(self, key: str, value: Any) -> None:
        """Update a specific context value."""
        self._context[key] = value
        self._context["last_updated"] = datetime.utcnow().isoformat()

    async def get_workflow_state(self) -> str:
        """Get the current workflow state."""
        return self._workflow_state

    async def set_workflow_state(self, state: str) -> None:
        """Set the current workflow state."""
        self._workflow_state = state
        await self.update_context("workflow_state", state)
