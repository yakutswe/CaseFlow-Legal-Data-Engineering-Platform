import asyncio

import httpx

from app.main import app


async def main():
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/health")

        print(response.status_code)
        print(response.json())


asyncio.run(main())