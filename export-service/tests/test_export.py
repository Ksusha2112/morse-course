import pytest


pytestmark = pytest.mark.usefixtures("client")


@pytest.fixture
def payload():
    return {"original": "Привет мир", "morse": ".--. .-. .. .-.. . - / -- .. .-."}


class TestExportTxt:
    def test_txt(self, client, payload):
        res = client.post("/api/export/txt", json=payload)
        assert res.status_code == 200
        assert "text/plain" in res.headers["content-type"]
        assert "Привет мир".encode("utf-8") in res.content

    def test_csv(self, client, payload):
        res = client.post("/api/export/csv", json=payload)
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]
        assert "Исходный текст".encode("utf-8") in res.content

    def test_pdf(self, client, payload):
        res = client.post("/api/export/pdf", json=payload)
        assert res.status_code == 200
        assert res.headers["content-type"] == "application/pdf"
        assert res.content.startswith(b"%PDF")

    def test_unknown_format_404(self, client, payload):
        res = client.post("/api/export/xml", json=payload)
        assert res.status_code == 404

    def test_missing_field_422(self, client):
        res = client.post("/api/export/txt", json={"original": "x"})
        assert res.status_code == 422

    def test_content_disposition(self, client, payload):
        res = client.post("/api/export/csv", json=payload)
        assert "morse_result.csv" in res.headers.get("content-disposition", "")


class TestHealth:
    def test_health(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["service"] == "export"
