import httpx

from ingestion.sources.supreme_court_source import SupremeCourtSource


def test_download_opinion_failure_isolated(monkeypatch):
    source = SupremeCourtSource()

    def fake_get_with_retry(url: str):
        raise httpx.HTTPError("forced failure")

    monkeypatch.setattr(
        source,
        "_get_with_retry",
        fake_get_with_retry,
    )

    result = source._download_opinion(
        {
            "external_id": "scotus-test",
            "case_name": "Test Case",
            "court_id": 1,
            "decision_date": "10/01/26",
            "docket_number": "TEST-1",
            "source_url": "https://example.com/test.pdf",
        }
    )

    assert result is None