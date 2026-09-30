from typing import Any

import httpx

from app.core.config import settings
from ingestion.sources.base import LegalSource


class CourtListenerSource(LegalSource):
    BASE_URL = "https://www.courtlistener.com/api/rest/v4/search/"

    def __init__(
        self,
        query: str,
        *,
        court_id: int = 1,
    ):
        self.query = query
        self.court_id = court_id

    def fetch(self) -> list[dict[str, Any]]:
        headers = {
            "Authorization": (
                f"Token {settings.courtlistener_api_token}"
            ),
            "User-Agent": "CaseFlow/0.1",
        }

        params = {
            "q": self.query,
            "type": "o",
        }

        response = httpx.get(
            self.BASE_URL,
            params=params,
            headers=headers,
            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        records: list[dict[str, Any]] = []

        for item in results:
            records.append(
                {
                    "external_id": (
                        f"courtlistener-{item.get('id')}"
                    ),
                    "case_name": (
                        item.get("caseName")
                        or item.get("case_name")
                        or "Unknown Case"
                    ),
                    "court_id": self.court_id,
                    "decision_date": item.get("dateFiled"),
                    "docket_number": item.get(
                        "docketNumber"
                    ),
                    "opinion_text": (
                        item.get("snippet")
                        or item.get("text")
                        or ""
                    ),
                    "source_url": (
                        "https://www.courtlistener.com"
                        + item.get("absolute_url", "")
                    ),
                }
            )

        return records