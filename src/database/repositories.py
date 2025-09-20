from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Measurement, User


class UserRepository:
    """Repository for user data operations."""

    def __init__(self, session: Session):
        self.session = session

    def create_user(
        self, telegram_id: int, username: str | None = None, first_name: str | None = None
    ) -> User | None:
        """Create a new user or return existing one."""
        existing_user = self.get_by_telegram_id(telegram_id)
        if existing_user:
            return existing_user

        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            registered_at=datetime.utcnow(),
        )

        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except IntegrityError:
            self.session.rollback()
            return self.get_by_telegram_id(telegram_id)

    def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID."""
        return self.session.query(User).filter(User.telegram_id == telegram_id).first()

    def get_all_users(self) -> list[User]:
        """Get all registered users."""
        return self.session.query(User).all()


class MeasurementRepository:
    """Repository for measurement data operations."""

    def __init__(self, session: Session):
        self.session = session

    def create_measurement(
        self, user_id: int, systolic: int, diastolic: int, measured_at: datetime | None = None
    ) -> Measurement:
        """Create a new blood pressure measurement."""
        measurement = Measurement(
            user_id=user_id,
            systolic=systolic,
            diastolic=diastolic,
            measured_at=measured_at or datetime.utcnow(),
        )

        self.session.add(measurement)
        self.session.commit()
        self.session.refresh(measurement)
        return measurement

    def get_user_measurements(self, user_id: int) -> list[Measurement]:
        """Get all measurements for a specific user."""
        return (
            self.session.query(Measurement)
            .filter(Measurement.user_id == user_id)
            .order_by(Measurement.measured_at.desc())
            .all()
        )

    def get_recent_measurements(self, user_id: int, limit: int = 10) -> list[Measurement]:
        """Get recent measurements for a user."""
        return (
            self.session.query(Measurement)
            .filter(Measurement.user_id == user_id)
            .order_by(Measurement.measured_at.desc())
            .limit(limit)
            .all()
        )

    def get_daily_measurement_count(self, user_id: int, target_date: date) -> int:
        """Get count of measurements for a specific user on a given date."""
        return (
            self.session.query(Measurement)
            .filter(
                Measurement.user_id == user_id, func.date(Measurement.measured_at) == target_date
            )
            .count()
        )


def get_repositories(session: Session) -> tuple[UserRepository, MeasurementRepository]:
    """Get repository instances for the session."""
    return UserRepository(session), MeasurementRepository(session)
