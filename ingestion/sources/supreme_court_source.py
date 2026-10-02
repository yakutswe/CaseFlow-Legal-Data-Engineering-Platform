import time

from concurrent.futures import ThreadPoolExecutor
from typing import Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from ingestion.parsers.pdf_parser import extract_pdf_text
from ingestion.sources.http_source import HttpLegalSource


class SupremeCourtSource(HttpLegalSource):
    BASE_URL = "https://www.supremecourt.gov"

    MAX_WORKERS = 8
    MAX_RETRIES = 3
    REQUEST_TIMEOUT = 20.0

    def __init__(self):
        super().__init__(
            url=(
                "https://www.supremecourt.gov/"
                "opinions/slipopinions.aspx?Term=25"
            )
        )

    def _get_with_retry(
        self,
        url: str,
    ) -> httpx.Response:
        last_error: Exception | None = None

        for attempt in range(
            1,
            self.MAX_RETRIES + 1,
        ):
            try:
                response = httpx.get(
                    url,
                    timeout=self.REQUEST_TIMEOUT,
                    follow_redirects=True,
                    headers={
                        "User-Agent": "CaseFlow/0.1"
                    },
                )

                response.raise_for_status()

                return response

            except (
                httpx.HTTPError,
                httpx.TimeoutException,
            ) as exc:
                last_error = exc

                if attempt == self.MAX_RETRIES:
                    break

                delay = 2 ** (attempt - 1)

                print(
                    f"Retrying {url} "
                    f"attempt={attempt + 1} "
                    f"after={delay}s "
                    f"error={exc}"
                )

                time.sleep(delay)

        raise RuntimeError(
            f"Request failed after "
            f"{self.MAX_RETRIES} attempts: {url}"
        ) from last_error

    def fetch_text(self) -> str:
        response = self._get_with_retry(
            self.url
        )

        return response.text

    def _download_opinion(
        self,
        metadata: dict[str, Any],
    ) -> dict[str, Any] | None:
        source_url = metadata["source_url"]

        try:
            pdf_response = self._get_with_retry(
                source_url
            )

            opinion_text = extract_pdf_text(
                pdf_response.content
            )

        except Exception as exc:
            print(
                f"Failed PDF: {source_url} "
                f"error={exc}"
            )

            return None

        if not opinion_text:
            print(
                f"Empty PDF text: {source_url}"
            )

            return None

        return {
            **metadata,
            "opinion_text": opinion_text,
        }

    def fetch(self) -> list[dict[str, Any]]:
        html = self.fetch_text()

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        metadata_records: list[
            dict[str, Any]
        ] = []

        rows = soup.select("table tr")

        for row in rows:
            cells = row.find_all("td")

            if len(cells) < 4:
                continue

            date_text = cells[1].get_text(
                " ",
                strip=True,
            )

            docket_number = cells[2].get_text(
                " ",
                strip=True,
            )

            name_cell = cells[3]

            case_name = name_cell.get_text(
                " ",
                strip=True,
            )

            link = name_cell.find("a")

            if (
                not docket_number
                or not case_name
                or link is None
            ):
                continue

            href = link.get("href")

            if not isinstance(href, str):
                continue

            source_url = urljoin(
                self.BASE_URL,
                href,
            )

            metadata_records.append(
                {
                    "external_id": (
                        f"scotus-{docket_number}"
                    ),
                    "case_name": case_name,
                    "court_id": 1,
                    "decision_date": date_text,
                    "docket_number":
                        docket_number,
                    "source_url": source_url,
                }
            )

        if not metadata_records:
            raise RuntimeError(
                "Supreme Court page loaded, "
                "but zero opinion metadata "
                "records were parsed"
            )

        records: list[
            dict[str, Any]
        ] = []

        with ThreadPoolExecutor(
            max_workers=self.MAX_WORKERS
        ) as executor:
            results = executor.map(
                self._download_opinion,
                metadata_records,
            )

            for result in results:
                if result is not None:
                    records.append(result)

        if not records:
            raise RuntimeError(
                "Supreme Court metadata was "
                "parsed, but zero opinion PDFs "
                "were successfully processed"
            )

        print(
            "Supreme Court ingestion: "
            f"metadata={len(metadata_records)} "
            f"successful={len(records)} "
            f"failed="
            f"{len(metadata_records) - len(records)}"
        )

        return records