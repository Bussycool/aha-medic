import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from database_config import Base


if TYPE_CHECKING:
  from modules.users.models.user_model import User
  


class Record(Base):
  __tablename__ = "records"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  note: Mapped[str] = mapped_column(Text, nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

  # relationships
  patient_id: Mapped[UUID(as_uuid=True)] = mapped_column(ForeignKey("users.id"))
  patient: Mapped["User"] = relationship("User", foreign_keys=[patient_id], backref="patient_records")

  staff_id: Mapped[UUID(as_uuid=True)] = mapped_column(ForeignKey("users.id"))
  staff: Mapped["User"] = relationship("User", foreign_keys=[staff_id], backref="staff_records")
