import pytest

from app.main import app as fastapi_app, update_stats


@pytest.fixture
def app():
    fastapi_app.dependency_overrides.clear()
    return fastapi_app


@pytest.fixture(autouse=True)
def disable_stats(monkeypatch):
    async def noop(direction: str) -> None:
        return None

    monkeypatch.setattr("app.main.update_stats", noop)


@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c
