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

        return cls(
            telegram_token=telegram_token,
            database_url=database_url,
            reminder_times=reminder_times,
            debug=debug
        )


# Global settings instance
settings = Settings.from_env()
