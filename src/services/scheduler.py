import asyncio
import logging
from datetime import datetime, time, timedelta, timezone

from aiogram import Bot

from ..config.settings import settings
from ..database.database import get_database
from ..database.repositories import get_repositories

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """Service for scheduling and sending blood pressure measurement reminders."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.running = False
        # MSK timezone (UTC+3)
        self.msk_tz = timezone(timedelta(hours=3))

    async def start(self) -> None:
        """Start the reminder scheduler."""
        self.running = True
        logger.info("Reminder scheduler started")

        # Create tasks for each reminder time
        tasks = []
        for reminder_time in settings.reminder_times:
            task = asyncio.create_task(self._schedule_daily_reminder(reminder_time))
            tasks.append(task)

        # Wait for all tasks (they run forever until stopped)
        await asyncio.gather(*tasks, return_exceptions=True)

    def stop(self) -> None:
        """Stop the reminder scheduler."""
        self.running = False
        logger.info("Reminder scheduler stopped")

    async def _schedule_daily_reminder(self, reminder_time: str) -> None:
        """Schedule daily reminders for a specific time."""
        try:
            hour, minute = map(int, reminder_time.split(':'))
            target_time = time(hour, minute)
        except ValueError:
            logger.error(f"Invalid reminder time format: {reminder_time}")
            return

        logger.info(f"Scheduled daily reminder for {reminder_time} MSK")

        while self.running:
            # Get current time in MSK
            now_msk = datetime.now(self.msk_tz)

            # Create target datetime in MSK
            target_datetime_msk = datetime.combine(
                now_msk.date(),
                target_time,
                tzinfo=self.msk_tz
            )

            # If target time has passed today, schedule for tomorrow
            if target_datetime_msk <= now_msk:
                tomorrow_msk = now_msk.date() + timedelta(days=1)
                target_datetime_msk = datetime.combine(
                    tomorrow_msk,
                    target_time,
                    tzinfo=self.msk_tz
                )

            # Calculate sleep duration
            sleep_duration = (target_datetime_msk - now_msk).total_seconds()

            logger.debug(f"Next reminder at {target_datetime_msk} MSK (sleeping {sleep_duration}s)")

            try:
                await asyncio.sleep(sleep_duration)
                if self.running:  # Check if still running after sleep
                    await self._send_reminders()
            except asyncio.CancelledError:
                logger.info(f"Reminder task for {reminder_time} cancelled")
                break
            except Exception as e:
                logger.error(f"Error in reminder scheduler: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def _send_reminders(self) -> None:
        """Send reminder messages to all registered users."""
        logger.info("Sending reminder messages")

        try:
            db = get_database()

            with db.get_session() as session:
                user_repo, _ = get_repositories(session)
                users = user_repo.get_all_users()

                reminder_message = (
                    "🩺 Время измерить артериальное давление!" # \n\n"
                    # "Пожалуйста, измерьте артериальное давление и отправьте мне результат.\n"
                    # "Формат: 120/80"
                )

                sent_count = 0
                failed_count = 0

                for user in users:
                    try:
                        await self.bot.send_message(
                            chat_id=user.telegram_id,
                            text=reminder_message
                        )
                        sent_count += 1

                        # Small delay to avoid hitting rate limits
                        await asyncio.sleep(0.1)

                    except Exception as e:
                        logger.error(f"Failed to send reminder to user {user.telegram_id}: {e}")
                        failed_count += 1

                logger.info(f"Reminders sent: {sent_count}, failed: {failed_count}")

        except Exception as e:
            logger.error(f"Error sending reminders: {e}")

    async def send_test_reminder(self, telegram_id: int) -> bool:
        """Send a test reminder to a specific user."""
        try:
            await self.bot.send_message(
                chat_id=telegram_id,
                text="🧪 Тестовое напоминание: Время измерить артериальное давление!"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send test reminder to {telegram_id}: {e}")
            return False
