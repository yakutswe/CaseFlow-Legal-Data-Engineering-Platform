from typing import Any

from ingestion.sources.base import LegalSource


class SampleLegalSource(LegalSource):
    def fetch(self) -> list[dict[str, Any]]:
        return [
            {
                "external_id": "sample-case-001",
                "case_name": "Sample Case One",
                "court_id": 1,
                "decision_date": "1970-01-01",
                "docket_number": "100",
                "opinion_text": "This is sample legal opinion text.",
                "source_url": "https://example.com/sample-case-001",
            }
        ]