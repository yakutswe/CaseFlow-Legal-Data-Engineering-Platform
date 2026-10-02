import pytest
import httpx

from app.main import app


@pytest.mark.anyio
async def test_search_endpoint():
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/search",
            params={
                "q": "standing",
                "limit": 5,
                "offset": 0,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 5

    if data:
        first = data[0]

        assert "case_id" in first
        assert "case_name" in first
        assert "rank" in first
        assert "snippet" in first