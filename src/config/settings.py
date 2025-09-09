import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Application settings from environment variables."""

    # Telegram Bot Configuration
    telegram_token: str

    # Database Configuration
    database_url: str

    # Reminder Times (24-hour format)
    reminder_times: list[str]

    # Authorized requesters for cross-user reports
    authorized_requesters: list[int]

    # Application Settings
    debug: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables."""
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        if not telegram_token:
            raise ValueError("TELEGRAM_TOKEN environment variable is required")

        database_url = os.getenv("DATABASE_URL", "sqlite:///blood_pressure.db")

        reminder_times_str = os.getenv("REMINDER_TIMES", "07:00,13:00,20:00")
        reminder_times = [time.strip() for time in reminder_times_str.split(",")]

        debug = os.getenv("DEBUG", "false").lower() == "true"

        # Parse authorized requesters (comma-separated telegram IDs)
        authorized_requesters_str = os.getenv("AUTHORIZED_REQUESTERS", "")
        authorized_requesters = []
        if authorized_requesters_str.strip():
            try:
                authorized_requesters = [int(telegram_id.strip()) for telegram_id in authorized_requesters_str.split(",") if telegram_id.strip()]
            except ValueError as e:
                raise ValueError("AUTHORIZED_REQUESTERS must contain comma-separated telegram IDs") from e

        return cls(
            telegram_token=telegram_token,
            database_url=database_url,
            reminder_times=reminder_times,
            debug=debug,
            authorized_requesters=authorized_requesters
        )


# Global settings instance
settings = Settings.from_env()
