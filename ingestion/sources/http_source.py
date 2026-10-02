import time
from typing import Any

import httpx

from ingestion.sources.base import LegalSource


class HttpLegalSource(LegalSource):
    def __init__(
        self,
        url: str,
        *,
        timeout: float = 10.0,
        max_retries: int = 3,
    ):
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
def fetch_text(self) -> str:
    last_error: Exception | None = None

    for attempt in range(
        1,
        self.max_retries + 1,
    ):
        try:
            response = httpx.get(
                self.url,
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "CaseFlow/0.1"
                },
            )

            response.raise_for_status()

            if not response.text.strip():
                raise RuntimeError(
                    "Source returned empty response"
                )

            return response.text

        except (
            httpx.TimeoutException,
            httpx.HTTPError,
            RuntimeError,
        ) as exc:
            last_error = exc

            if attempt == self.max_retries:
                break

            time.sleep(
                2 ** (attempt - 1)
            )

    raise RuntimeError(
        f"Failed to fetch source after "
        f"{self.max_retries} attempts"
    ) from last_error


    def fetch_json(self) -> Any:
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = httpx.get(
                    self.url,
                    timeout=self.timeout,
                    headers={
                        "User-Agent": "CaseFlow/0.1"
                    },
                )

                response.raise_for_status()

                return response.json()

            except (
                httpx.TimeoutException,
                httpx.HTTPError,
                ValueError,
            ) as exc:
                last_error = exc

                if attempt == self.max_retries:
                    break

                time.sleep(2 ** (attempt - 1))

        raise RuntimeError(
            f"Failed to fetch source after "
            f"{self.max_retries} attempts"
        ) from last_error

    def fetch(self) -> list[dict[str, Any]]:
        raise NotImplementedError(
            "Subclasses must transform source data "
            "into CaseFlow records."
        )