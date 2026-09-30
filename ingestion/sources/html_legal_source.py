import time
from typing import Any

import httpx
from bs4 import BeautifulSoup

from ingestion.sources.base import LegalSource


class HtmlLegalSource(LegalSource):
    def __init__(
        self,
        url: str,
        *,
        court_id: int = 1,
        timeout: float = 10.0,
        max_retries: int = 3,
    ):
        self.url = url
        self.court_id = court_id
        self.timeout = timeout
        self.max_retries = max_retries

    def _fetch_html(self) -> str:
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
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
                        "Source returned empty HTML"
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

                time.sleep(2 ** (attempt - 1))

        raise RuntimeError(
            f"Failed to fetch HTML after "
            f"{self.max_retries} attempts"
        ) from last_error

    def fetch(self) -> list[dict[str, Any]]:
        html = self._fetch_html()

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        records: list[dict[str, Any]] = []

        for card in soup.select(".case-card"):
            external_id = card.get("data-case-id")

            case_name_element = card.select_one(
                ".case-name"
            )

            decision_date_element = card.select_one(
                ".decision-date"
            )

            docket_element = card.select_one(
                ".docket-number"
            )

            opinion_element = card.select_one(
                ".opinion-text"
            )

            link_element = card.select_one(
                "a.case-link"
            )

            if (
                not external_id
                or case_name_element is None
                or opinion_element is None
            ):
                continue

            records.append(
                {
                    "external_id": external_id,
                    "case_name": (
                        case_name_element.get_text(
                            " ",
                            strip=True,
                        )
                    ),
                    "court_id": self.court_id,
                    "decision_date": (
                        decision_date_element.get_text(
                            strip=True
                        )
                        if decision_date_element
                        else None
                    ),
                    "docket_number": (
                        docket_element.get_text(
                            " ",
                            strip=True,
                        )
                        if docket_element
                        else None
                    ),
                    "opinion_text": (
                        opinion_element.get_text(
                            " ",
                            strip=True,
                        )
                    ),
                    "source_url": (
                        link_element.get(
                            "href",
                            self.url,
                        )
                        if link_element
                        else self.url
                    ),
                }
            )

        if not records:
            raise RuntimeError(
                "HTML request succeeded but "
                "zero legal records were parsed"
            )

        return records