import io

import pytest

from app import main as app_main


pytestmark = pytest.mark.usefixtures("disable_stats")


class TestHealth:
    def test_health(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["service"] == "morse"
        assert data["version"]


class TestEncodeEndpoint:
    def test_encode_ok(self, client):
        res = client.post("/api/encode", json={"text": "SOS"})
        assert res.status_code == 200
        data = res.json()
        assert data["original"] == "SOS"
        assert data["morse"] == "... --- ..."

    def test_encode_cyrillic(self, client):
        res = client.post("/api/encode", json={"text": "Мир"})
        assert res.status_code == 200
        assert res.json()["morse"] == "-- .. .-."

    def test_encode_empty_text_400(self, client):
        res = client.post("/api/encode", json={"text": ""})
        assert res.status_code == 400

    def test_encode_whitespace_only_400(self, client):
        res = client.post("/api/encode", json={"text": "   "})
        assert res.status_code == 400

    def test_encode_missing_field_422(self, client):
        res = client.post("/api/encode", json={})
        assert res.status_code == 422


class TestDecodeEndpoint:
    def test_decode_ok(self, client):
        res = client.post("/api/decode", json={"morse": "... --- ..."})
        assert res.status_code == 200
        data = res.json()
        assert data["text"] == "SOS"
        assert data["morse"] == "... --- ..."

    def test_decode_empty_400(self, client):
        res = client.post("/api/decode", json={"morse": "  "})
        assert res.status_code == 400

    def test_decode_invalid_body_422(self, client):
        res = client.post("/api/decode", json={"text": "abc"})
        assert res.status_code == 422


class TestEncodeFileEndpoint:
    def _post_file(self, client, content: bytes, name="test.txt"):
        return client.post(
            "/api/encode-file",
            files={"file": (name, io.BytesIO(content), "text/plain")},
        )

    def test_utf8_file(self, client):
        res = self._post_file(client, "Привет".encode("utf-8"))
        assert res.status_code == 200
        data = res.json()
        assert data["original"] == "Привет"
        assert data["morse"]

    def test_cp1251_file(self, client):
        res = self._post_file(client, "Привет".encode("cp1251"))
        assert res.status_code == 200
        assert res.json()["original"] == "Привет"

    def test_empty_file_400(self, client):
        res = self._post_file(client, b"")
        assert res.status_code == 400

    def test_no_file_422(self, client):
        res = client.post("/api/encode-file")
        assert res.status_code == 422


class TestStatsIntegration:
    def test_stats_update_called(self, client, monkeypatch):
        import asyncio

        calls = []

        async def fake_update(direction: str) -> None:
            calls.append(direction)

        monkeypatch.setattr(app_main, "update_stats", fake_update)

        client.post("/api/encode", json={"text": "SOS"})
        client.post("/api/decode", json={"morse": "... --- ..."})
        assert calls == ["encode", "decode"]
