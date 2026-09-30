import re
from dataclasses import dataclass


@dataclass
class ParsedCitation:
    cited_case_name: str | None
    volume: int
    reporter: str
    page: int
    pin_cite: int | None
    year: int | None


CITATION_PATTERN = re.compile(
    r"""
    (?:(?P<case_name>[A-Z][A-Za-z0-9.&'’\-\s]+?\s+v\.\s+[A-Z][A-Za-z0-9.&'’\-\s]+?),\s+)?
    (?P<volume>\d{1,4})\s+
    (?P<reporter>U\.?\s*S\.?|F\.?\s*\d*d?|S\.?\s*Ct\.?)\s+
    (?P<page>\d{1,5})
    (?:,\s+(?P<pin_cite>\d{1,5}))?
    (?:\s+\((?P<year>\d{4})\))?
    """,
    re.VERBOSE,
)


def extract_citations(text: str) -> list[ParsedCitation]:
    citations: list[ParsedCitation] = []

    for match in CITATION_PATTERN.finditer(text):
        case_name = match.group("case_name")

        citations.append(
            ParsedCitation(
                cited_case_name=(
                    " ".join(case_name.split())
                    if case_name
                    else None
                ),
                volume=int(match.group("volume")),
                reporter=(
                    match.group("reporter")
                    .replace(" ", "")
                ),
                page=int(match.group("page")),
                pin_cite=(
                    int(match.group("pin_cite"))
                    if match.group("pin_cite")
                    else None
                ),
                year=(
                    int(match.group("year"))
                    if match.group("year")
                    else None
                ),
            )
        )

    return citations