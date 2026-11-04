"""Liveness and readiness endpoints.

/api/health        -> the process is up (used by the Docker health check).
/api/health/ready  -> each dependency is reachable, reported per component, so the UI
                      can show a clear message such as "Ollama is not running".
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Annotated, Literal

import httpx
from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from app.core.config import Settings, get_settings
from app.db.session import get_engine

router = APIRouter(prefix="/health", tags=["health"])


class ComponentStatus(BaseModel):
    status: Literal["ok", "error"]
    detail: str | None = None


class ReadinessReport(BaseModel):
    status: Literal["ok", "degraded"]
    components: dict[str, ComponentStatus]


class Liveness(BaseModel):
    status: Literal["ok"] = "ok"


async def check_postgres(settings: Settings) -> None:
    async with get_engine().connect() as conn:
        await conn.execute(text("SELECT 1"))


async def check_qdrant(settings: Settings) -> None:
    async with httpx.AsyncClient(timeout=settings.health_timeout_s) as client:
        (await client.get(f"{settings.qdrant_url}/readyz")).raise_for_status()


async def check_ollama(settings: Settings) -> None:
    try:
        async with httpx.AsyncClient(timeout=settings.health_timeout_s) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            resp.raise_for_status()
    except httpx.ConnectError as exc:
        raise RuntimeError(f"not reachable at {settings.ollama_base_url}; is Ollama running?") from exc
    installed = {m["name"] for m in resp.json().get("models", [])}
    missing = [
        m
        for m in (settings.llm_model, settings.embedding_model)
        if m not in installed and f"{m}:latest" not in installed
    ]
    if missing:
        raise RuntimeError(f"model(s) not pulled: {', '.join(missing)} (run `ollama pull <model>`)")


Check = Callable[[Settings], Awaitable[None]]


def get_checks() -> dict[str, Check]:
    return {"postgres": check_postgres, "qdrant": check_qdrant, "ollama": check_ollama}


async def _run(check: Check, settings: Settings) -> ComponentStatus:
    try:
        await asyncio.wait_for(check(settings), timeout=settings.health_timeout_s)
    except TimeoutError:
        return ComponentStatus(status="error", detail="timed out")
    except Exception as exc:  # report every failure as data; this endpoint must never crash
        return ComponentStatus(status="error", detail=str(exc) or type(exc).__name__)
    return ComponentStatus(status="ok")


@router.get("", response_model=Liveness)
async def liveness() -> Liveness:
    return Liveness()


@router.get("/ready", response_model=ReadinessReport)
async def readiness(
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
    checks: Annotated[dict[str, Check], Depends(get_checks)],
) -> ReadinessReport:
    names = list(checks)
    results = await asyncio.gather(*(_run(checks[n], settings) for n in names))
    components = dict(zip(names, results, strict=True))
    ok = all(c.status == "ok" for c in components.values())
    if not ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessReport(status="ok" if ok else "degraded", components=components)
