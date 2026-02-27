"""
API Routes — Health, status, and agent control endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()
_orchestrator = None


def set_orchestrator(orchestrator):
    global _orchestrator
    _orchestrator = orchestrator


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "arbitrage-agent", "version": "0.1.0"}


@router.get("/status")
async def agent_status():
    if not _orchestrator:
        return {"status": "not_initialized"}
    return _orchestrator.get_state()


@router.get("/integrations")
async def integration_health():
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return await _orchestrator.get_integration_health()


class RobinhoodLoginRequest(BaseModel):
    api_key: str
    private_key: str

@router.post("/integrations/robinhood/login")
async def robinhood_login(req: RobinhoodLoginRequest):
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    success = await _orchestrator.robinhood.update_credentials(req.api_key, req.private_key)
    if success:
        return {"status": "success", "message": "Robinhood authenticated"}
    else:
        raise HTTPException(status_code=401, detail="Authentication failed (check keys)")


@router.get("/portfolio")
async def portfolio():
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return await _orchestrator.robinhood.get_portfolio()


@router.get("/quotes/{asset_type}/{symbol}")
async def get_quote(asset_type: str, symbol: str):
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    if asset_type == "crypto":
        return (await _orchestrator.robinhood.get_crypto_quote(symbol)).model_dump()
    elif asset_type == "stock":
        return (await _orchestrator.robinhood.get_stock_quote(symbol)).model_dump()
    raise HTTPException(status_code=400, detail="asset_type must be 'crypto' or 'stock'")


@router.post("/agent/start")
async def start_agent():
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    await _orchestrator.start()
    return {"status": "started"}


@router.post("/agent/stop")
async def stop_agent():
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    await _orchestrator.stop()
    return {"status": "stopped"}


@router.post("/agent/cycle")
async def trigger_cycle():
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return await _orchestrator.run_single_cycle()


@router.get("/cycles")
async def get_cycles(limit: int = 10):
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return _orchestrator.get_cycle_logs(limit)


@router.get("/pnl")
async def get_pnl():
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return await _orchestrator.numeric.get_pnl()


@router.get("/graph/stats")
async def graph_stats():
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return await _orchestrator.neo4j.get_graph_stats()


@router.get("/model/status")
async def model_status():
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return await _orchestrator.fastino.get_model_status()


@router.get("/alerts")
async def get_alerts():
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return await _orchestrator.modulate.get_alert_history()
