from ingestion.parsers.citation_parser import extract_citations


def test_extract_citation():
    text = (
        "The Court discussed Brown v. Board of Education, "
        "347 U.S. 483 (1954)."
    )

    citations = extract_citations(text)

    assert len(citations) >= 1

    citation = citations[0]

    assert citation.volume == 347
    assert citation.reporter == "U.S."
    assert citation.page == 483
    assert citation.year == 1954
