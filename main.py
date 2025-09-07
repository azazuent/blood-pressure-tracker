import asyncio
import logging
import sys
from typing import NoReturn

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config.settings import settings
from src.database.database import init_database
from src.bot.handlers import router
from src.services.scheduler import ReminderScheduler


# Configure logging
import os
log_handlers = [logging.StreamHandler(sys.stdout)]

# Add file handler if logs directory exists or can be created
try:
    os.makedirs('logs', exist_ok=True)
    log_handlers.append(logging.FileHandler('logs/bot.log'))
except (OSError, PermissionError):
    # If can't create logs directory, just use stdout
    pass

logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)

logger = logging.getLogger(__name__)


async def main() -> NoReturn:
    """Main application entry point."""
    logger.info("Starting Blood Pressure Tracker Bot")
    
    try:
        # Initialize database
        logger.info(f"Initializing database: {settings.database_url}")
        init_database(settings.database_url)
        
        # Initialize bot and dispatcher
        bot = Bot(
            token=settings.telegram_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        dp = Dispatcher()
        dp.include_router(router)
        
        # Initialize reminder scheduler
        scheduler = ReminderScheduler(bot)
        
        # Start both bot polling and scheduler
        logger.info("Starting bot and scheduler...")
        
        async def start_polling():
            """Start bot polling."""
            await dp.start_polling(bot)
        
        async def start_scheduler():
            """Start reminder scheduler."""
            await scheduler.start()
        
        # Run both tasks concurrently
        await asyncio.gather(
            start_polling(),
            start_scheduler(),
            return_exceptions=True
        )
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)