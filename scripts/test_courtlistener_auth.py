import httpx

from app.core.config import settings


token = settings.courtlistener_api_token

if not token:
    raise RuntimeError("CourtListener token is missing")

response = httpx.get(
    "https://www.courtlistener.com/api/rest/v4/api-usage/",
    headers={
        "Authorization": f"Token {token.strip()}",
        "User-Agent": "CaseFlow/0.1",
    },
    timeout=15.0,
)

print("STATUS:", response.status_code)
print("BODY:", response.text)