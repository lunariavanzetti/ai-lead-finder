import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StaffMember(Base):
    __tablename__ = "staff_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), index=True)

    full_name: Mapped[str] = mapped_column(String(200))
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    is_decision_maker: Mapped[bool] = mapped_column(Boolean, default=False)
    priority_rank: Mapped[int] = mapped_column(Integer, default=99)  # lower = higher priority
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    lead: Mapped["Lead"] = relationship(back_populates="staff")
