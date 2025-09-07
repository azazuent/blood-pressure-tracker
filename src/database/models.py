from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    """User model for storing registered users."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    measurements = relationship("Measurement", back_populates="user", cascade="all, delete-orphan")


class Measurement(Base):
    """Blood pressure measurement model."""
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    systolic = Column(Integer, nullable=False)
    diastolic = Column(Integer, nullable=False)
    measured_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="measurements")

    @property
    def formatted_reading(self) -> str:
        """Return formatted blood pressure reading."""
        return f"{self.systolic}/{self.diastolic}"
