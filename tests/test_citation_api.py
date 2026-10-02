import pytest
import httpx

from app.main import app


@pytest.mark.anyio
async def test_case_citations_endpoint():
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/cases/36/citations"
        )

    assert response.status_code == 200

    data = response.json()

    print("STATUS:", response.status_code)
    print("BODY:", response.text)

    assert isinstance(data, list)

    if data:
        first = data[0]

        assert "id" in first
        assert "citing_case_id" in first
        assert "volume" in first
        assert "reporter" in first
        assert "page" in first       