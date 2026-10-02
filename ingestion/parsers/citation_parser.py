from dataclasses import dataclass

from eyecite import get_citations
from eyecite.models import FullCaseCitation


@dataclass
class ParsedCitation:
    cited_case_name: str | None
    volume: int
    reporter: str
    page: int
    pin_cite: int | None
    year: int | None


def normalize_case_name(
    plaintiff: str | None,
    defendant: str | None,
) -> str | None:
    if not plaintiff or not defendant:
        return None

    plaintiff = " ".join(
        plaintiff.split()
    ).strip()

    defendant = " ".join(
        defendant.split()
    ).strip()

    if not plaintiff or not defendant:
        return None

    return f"{plaintiff} v. {defendant}"


def extract_citations(
    text: str,
) -> list[ParsedCitation]:
    results: list[ParsedCitation] = []

    citations = get_citations(text)

    for citation in citations:
        if not isinstance(
            citation,
            FullCaseCitation,
        ):
            continue

        groups = citation.groups
        metadata = citation.metadata

        volume = groups.get("volume")
        reporter = groups.get("reporter")
        page = groups.get("page")

        if not volume or not reporter or not page:
            continue

        plaintiff = getattr(
            metadata,
            "plaintiff",
            None,
        )

        defendant = getattr(
            metadata,
            "defendant",
            None,
        )

        year = getattr(
            metadata,
            "year",
            None,
        )

        pin_cite = getattr(
            metadata,
            "pin_cite",
            None,
        )

        try:
            pin_value = (
                int(pin_cite)
                if pin_cite
                and str(pin_cite).isdigit()
                else None
            )
        except (TypeError, ValueError):
            pin_value = None

        results.append(
            ParsedCitation(
                cited_case_name=normalize_case_name(
                    plaintiff,
                    defendant,
                ),
                volume=int(volume),
                reporter=str(reporter),
                page=int(page),
                pin_cite=pin_value,
                year=(
                    int(year)
                    if year
                    else None
                ),
            )
        )

    return results