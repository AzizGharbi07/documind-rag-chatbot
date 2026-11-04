import pytest

from app.core.config import Settings


def test_env_overrides_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "llama3.2:3b")
    monkeypatch.setenv("CORS_ORIGINS", '["http://a", "http://b"]')
    settings = Settings(_env_file=None)
    assert settings.llm_model == "llama3.2:3b"
    assert settings.cors_origins == ["http://a", "http://b"]
