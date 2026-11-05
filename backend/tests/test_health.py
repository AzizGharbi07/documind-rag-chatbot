import asyncio
from collections.abc import Callable

import httpx
import pytest
from fastapi import FastAPI

from app.api.health import Check, check_ollama, get_checks
from app.core.config import Settings, get_settings


async def _ok(_: Settings) -> None:
    return None


async def _boom(_: Settings) -> None:
    raise ConnectionError("connection refused")


async def _slow(_: Settings) -> None:
    await asyncio.sleep(10)


def _use_checks(app: FastAPI, checks: dict[str, Check]) -> None:
    app.dependency_overrides[get_checks] = lambda: checks


async def test_liveness(client: httpx.AsyncClient) -> None:
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_ready_all_ok(app: FastAPI, client: httpx.AsyncClient) -> None:
    _use_checks(app, {"postgres": _ok, "ollama": _ok})
    resp = await client.get("/api/health/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_ready_reports_failing_component(app: FastAPI, client: httpx.AsyncClient) -> None:
    _use_checks(app, {"postgres": _ok, "ollama": _boom})
    resp = await client.get("/api/health/ready")
    body = resp.json()
    assert resp.status_code == 503
    assert body["status"] == "degraded"
    assert body["components"]["postgres"]["status"] == "ok"
    assert body["components"]["ollama"] == {"status": "error", "detail": "connection refused"}


def _mock_http(monkeypatch: pytest.MonkeyPatch, handler: Callable[[httpx.Request], httpx.Response]) -> None:
    """Route every httpx.AsyncClient through an in-memory handler: no real network in unit tests."""
    real_client = httpx.AsyncClient
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: real_client(transport=transport, **kw))


async def test_ollama_check_explains_unreachable_server(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("All connection attempts failed", request=request)

    _mock_http(monkeypatch, refuse)
    settings = Settings(ollama_base_url="http://ollama.test:11434")
    with pytest.raises(
        RuntimeError, match=r"not reachable at http://ollama\.test:11434; is Ollama running\?"
    ):
        await check_ollama(settings)


async def test_ollama_check_lists_missing_models(monkeypatch: pytest.MonkeyPatch) -> None:
    tags = {"models": [{"name": "qwen2.5:3b"}]}
    _mock_http(monkeypatch, lambda _: httpx.Response(200, json=tags))

    settings = Settings(llm_model="qwen2.5:3b", embedding_model="bge-m3")
    with pytest.raises(RuntimeError, match="model\\(s\\) not pulled: bge-m3"):
        await check_ollama(settings)


async def test_ready_times_out_slow_component(app: FastAPI, client: httpx.AsyncClient) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(health_timeout_s=0.05)
    _use_checks(app, {"qdrant": _slow})
    resp = await client.get("/api/health/ready")
    assert resp.status_code == 503
    assert resp.json()["components"]["qdrant"]["detail"] == "timed out"
