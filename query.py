from httpx import AsyncClient

RAY_SERVE_ADDRESS = "HERE"


async def send_request(deployment_name: str) -> int:
    async with AsyncClient() as client:
        response = await client.get(
            f"http://{RAY_SERVE_ADDRESS}:8000/deployment_name",
            timeout=3,
        )
        response.raise_for_status()
    return response.json()["count"]
