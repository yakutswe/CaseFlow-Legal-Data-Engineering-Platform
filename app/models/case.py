from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.court import Court


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)

    external_id: Mapped[str] = mapped_column(
                String(255),
                unique=True,
                nullable=False,
                index=True,
    )

    case_name: Mapped[str] = mapped_column(
                String(500),
                nullable=False,
                index=True,
    )
    court_id: Mapped[int] = mapped_column(
        ForeignKey("courts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    decision_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        index=True,
    )

    docket_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    opinion_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    court: Mapped["Court"] = relationship(
        back_populates="cases",
    )