from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    citing_case_id: Mapped[int] = mapped_column(
        ForeignKey(
            "cases.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    cited_case_name: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    volume: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reporter: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    page: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    pin_cite: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )