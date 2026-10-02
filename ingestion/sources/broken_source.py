from typing import Any

from ingestion.sources.base import LegalSource


class BrokenSource(LegalSource):
    def fetch(self) -> list[dict[str, Any]]:
        return []