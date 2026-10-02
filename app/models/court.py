from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base 

if TYPE_CHECKING:
    from app.models.case import Case

class Court(Base):
    
    __tablename__ = "courts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    abbreviation: Mapped[str] = mapped_column(String(50),unique=True, nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(100),nullable=False)
    level: Mapped[str] = mapped_column(String(50), nullable=False)

    cases: Mapped[list["Case"]] = relationship(
    back_populates="court", cascade="all, delete-orphan")