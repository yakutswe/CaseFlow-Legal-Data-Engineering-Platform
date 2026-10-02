from typing import cast

import pytest
from sqlalchemy.orm import Session

from ingestion.pipelines.source_pipeline import LegalSource, ingest_source


class BrokenSource:
    name = "broken-source"

    def fetch(self):
        return []


def test_suspicious_low_record_count():
    source = BrokenSource()

    with pytest.raises(
        RuntimeError,
        match="Suspiciously low record count",
    ):
        ingest_source(
            source=cast(LegalSource, source),
            db=cast(Session, None),
            min_expected_records=10,
        )