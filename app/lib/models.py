from app.lib.database import Base
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class ArchiveRecord(Base):
    __tablename__ = "archive_records"

    profile_name: Mapped[str] = mapped_column(Text, nullable=False)
    record_url: Mapped[str] = mapped_column(Text, nullable=False)
    archive_link: Mapped[str] = mapped_column(Text, nullable=False)
    domain_type: Mapped[str] = mapped_column(String(100), nullable=False)
    first_capture_display: Mapped[str] = mapped_column(String(100), nullable=False)
    latest_capture_display: Mapped[str] = mapped_column(String(100), nullable=False)
    ongoing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    wam_id: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Computed fields for sorting and filtering
    sort_name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    first_character: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    record_hash: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    def __repr__(self):
        return f"<ArchiveRecord(id={self.id}, wam_id={self.wam_id})>"
