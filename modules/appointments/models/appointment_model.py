import uuid
from datetime import datetime, time, date

from sqlalchemy import Column, DateTime, Enum, Time, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database_config import Base
from ..enums.appointment_status import Appointment_Status

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from modules.users.models.user_model import User


class Appointment(Base):
  __tablename__ = "appointments"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  booking_date: Mapped[date] = mapped_column(Date, nullable=False)
  start_time: Mapped[time] = mapped_column(Time, nullable=False)
  end_time: Mapped[time] = mapped_column(Time, nullable=False)
  status: Mapped[Appointment_Status] = mapped_column(Enum(Appointment_Status), default=Appointment_Status.BOOKED)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

  # relationship
  patient_id: Mapped[UUID(as_uuid=True)] = mapped_column(ForeignKey("users.id"))
  patient: Mapped["User"] = relationship("User", foreign_keys=[patient_id], backref="patient_appointments")
  
  staff_id: Mapped[UUID(as_uuid=True)] = mapped_column(ForeignKey("users.id"))
  staff: Mapped["User"] = relationship("User", foreign_keys=[staff_id], backref="staff_appointments")

