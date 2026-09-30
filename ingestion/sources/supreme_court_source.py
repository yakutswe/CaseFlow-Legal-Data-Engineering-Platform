import httpx

from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ingestion.parsers.pdf_parser import extract_pdf_text
from ingestion.sources.http_source import HttpLegalSource


class SupremeCourtSource(HttpLegalSource):
    BASE_URL = "https://www.supremecourt.gov"

    def __init__(self):
        super().__init__(
            url=(
                "https://www.supremecourt.gov/"
                "opinions/slipopinions.aspx?Term=25"
            )
        )

    def fetch_text(self) -> str:
        response = httpx.get(
            self.url,
            timeout=20.0,
            follow_redirects=True,
            headers={"User-Agent": "CaseFlow/0.1"},
        )
        response.raise_for_status()
        return response.text

    def fetch(self) -> list[dict[str, Any]]:
        html = self.fetch_text()

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        records: list[dict[str, Any]] = []

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

            try:
                pdf_response = httpx.get(
                    source_url,
                    timeout=20.0,
                    follow_redirects=True,
                    headers={
                        "User-Agent": "CaseFlow/0.1"
                    },
                )

                pdf_response.raise_for_status()

                opinion_text = extract_pdf_text(
                    pdf_response.content
                )

            except Exception as exc:
                print(
                    f"Failed PDF: {source_url} "
                    f"error={exc}"
                )
                continue

            if not opinion_text:
                continue

            records.append(
                {
                    "external_id": (
                        f"scotus-{docket_number}"
                    ),
                    "case_name": case_name,
                    "court_id": 1,
                    "decision_date": date_text,
                    "docket_number": docket_number,
                    "opinion_text": opinion_text,
                    "source_url": source_url,
                }
            )

        if not records:
            raise RuntimeError(
                "Supreme Court page loaded, "
                "but zero opinion records were parsed"
            )

        return records