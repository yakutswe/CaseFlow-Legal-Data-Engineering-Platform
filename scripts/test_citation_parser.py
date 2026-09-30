from ingestion.parsers.citation_parser import (
    extract_citations,
)


text = """
To secure a stay, see Nken v. Holder,
556 U.S. 418, 434 (2009).

Standing also requires injury.
See TransUnion LLC v. Ramirez,
594 U.S. 413, 423 (2021).
"""


citations = extract_citations(text)

for citation in citations:
    print(citation)