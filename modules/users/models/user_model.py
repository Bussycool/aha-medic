import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database_config import Base
from ..enums.role_enum import Role


class User(Base):
  __tablename__ = "users"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  email: Mapped[str] = mapped_column(
    String(50), unique=True, index=True, nullable=False
  )
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  password: Mapped[str] = mapped_column(String(100), nullable=False)
  role: Mapped[Role] = mapped_column(Enum(Role), default=Role.PATIENT)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

