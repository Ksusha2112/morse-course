import pytest


@pytest.fixture
def client(client):
    return client


class TestIncrement:
    def test_increment_encode(self, client):
        res = client.post("/api/increment", json={"direction": "encode"})
        assert res.status_code == 200
        stats = client.get("/api/stats").json()
        assert stats["encodes"] == 1
        assert stats["decodes"] == 0
        assert stats["total"] == 1

    def test_increment_decode(self, client):
        client.post("/api/increment", json={"direction": "decode"})
        stats = client.get("/api/stats").json()
        assert stats["decodes"] == 1

    def test_increment_unknown_direction_400(self, client):
        res = client.post("/api/increment", json={"direction": "foo"})
        assert res.status_code == 400

    def test_increment_missing_field_422(self, client):
        res = client.post("/api/increment", json={})
        assert res.status_code == 422

    def test_counters_accumulate(self, client):
        for _ in range(3):
            client.post("/api/increment", json={"direction": "encode"})
        client.post("/api/increment", json={"direction": "decode"})
        stats = client.get("/api/stats").json()
        assert stats["encodes"] == 3
        assert stats["decodes"] == 1
        assert stats["total"] == 4


class TestStats:
    def test_stats_initial_zero(self, client):
        stats = client.get("/api/stats").json()
        assert stats == {"encodes": 0, "decodes": 0, "total": 0}


class TestHealth:
    def test_health(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"
