import re
from datetime import date, datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from ..config.settings import settings
from ..database.database import get_database
from ..database.repositories import get_repositories
from ..services.report_generator import ReportGenerator

router = Router()


def get_reminder_times_text() -> str:
    """Get formatted reminder times text."""
    times = ", ".join(settings.reminder_times)
    return f"в {times} ежедневно (МСК)"


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    """Handle /start command and register user."""
    db = get_database()

    with db.get_session() as session:
        user_repo, _ = get_repositories(session)

        user = user_repo.create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )

        if user:
            await message.answer(
                "Добро пожаловать в Трекер Артериального Давления! 🩺\n\n"
                "Я помогу вам отслеживать показания артериального давления.\n\n"
                "Команды:\n"
                "• Отправьте мне показания в формате: 120/80\n"
                "• /report - Получить измерения в виде CSV\n"
                "• /help - Показать справку\n\n"
                f"Я буду отправлять напоминания {get_reminder_times_text()}."
            )
        else:
            await message.answer("Регистрация не удалась. Пожалуйста, попробуйте снова.")


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    """Handle /help command."""
    await message.answer(
        "Команды Трекера Артериального Давления:\n\n"
        "📊 Запись измерений:\n"
        "• Отправьте показания: 120/80\n"
        "• Формат: систолическое/диастолическое\n\n"
        "📋 Отчеты:\n"
        "• /report - Скачать CSV со всеми измерениями\n\n"
        "ℹ️ Другое:\n"
        "• /help - Показать это сообщение\n\n"
        f"💡 Я буду напоминать измерять давление {get_reminder_times_text()}."
    )


@router.message(Command("report"))
async def report_command(message: Message) -> None:
    """Handle /report command - generate CSV report."""
    db = get_database()

    with db.get_session() as session:
        user_repo, measurement_repo = get_repositories(session)

        user = user_repo.get_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("Пожалуйста, используйте /start для регистрации.")
            return

        measurements = measurement_repo.get_user_measurements(user.id)

        if not measurements:
            await message.answer("Измерения не найдены. Сначала запишите несколько показаний!")
            return

        report_generator = ReportGenerator()
        csv_data = report_generator.generate_csv_report(measurements)

        # Create file name with current date
        filename = f"bp_report_{datetime.now().strftime('%Y%m%d')}.csv"

        # Send CSV as document
        from aiogram.types import BufferedInputFile

        file = BufferedInputFile(csv_data.encode(), filename)

        await message.answer_document(
            document=file,
            caption=f"📊 Ваш отчет по артериальному давлению ({len(measurements)} измерений)",
        )


@router.message(F.text.regexp(r"^/report_(\d+)$"))
async def report_user_command(message: Message) -> None:
    """Handle /report_<user_id> command - generate CSV report for another user."""
    # Check if requester is authorized
    if message.from_user.id not in settings.authorized_requesters:
        await message.answer("❌ У вас нет прав для запроса отчетов других пользователей.")
        return

    # Extract target user ID from command
    match = re.match(r"^/report_(\d+)$", message.text)
    if not match:
        await message.answer("❌ Неверный формат команды. Используйте /report_<telegram_id>")
        return

    target_telegram_id = int(match.group(1))

    db = get_database()

    with db.get_session() as session:
        user_repo, measurement_repo = get_repositories(session)

        # Find target user by telegram ID
        target_user = user_repo.get_by_telegram_id(target_telegram_id)
        if not target_user:
            await message.answer(f"❌ Пользователь с ID {target_telegram_id} не найден.")
            return

        measurements = measurement_repo.get_user_measurements(target_user.id)

        if not measurements:
            await message.answer(f"❌ У пользователя {target_telegram_id} нет измерений.")
            return

        report_generator = ReportGenerator()
        csv_data = report_generator.generate_csv_report(measurements)

        # Create file name with user ID and current date
        filename = f"bp_report_{target_telegram_id}_{datetime.now().strftime('%Y%m%d')}.csv"

        # Send CSV as document
        from aiogram.types import BufferedInputFile

        file = BufferedInputFile(csv_data.encode(), filename)

        await message.answer_document(
            document=file,
            caption=f"📊 Отчет пользователя {target_telegram_id} ({len(measurements)} измерений)",
        )


def parse_blood_pressure(text: str) -> tuple[int, int] | None:
    """Parse blood pressure reading from text."""
    # Match patterns like "120/80", "120 / 80", "120-80"
    pattern = r"(\d{2,3})\s*[/\-]\s*(\d{2,3})"
    match = re.search(pattern, text)

    if match:
        systolic = int(match.group(1))
        diastolic = int(match.group(2))

        # Basic validation
        if 60 <= systolic <= 250 and 30 <= diastolic <= 150 and systolic > diastolic:
            return systolic, diastolic

    return None


@router.message(F.text)
async def handle_measurement(message: Message) -> None:
    """Handle blood pressure measurement input."""
    db = get_database()

    # Try to parse blood pressure reading
    reading = parse_blood_pressure(message.text)

    if not reading:
        await message.answer(
            "❌ Неверный формат. Пожалуйста, отправьте показания так:\n"
            "• 120/80\n"
            "• 130/85\n\n"
            "Используйте /help для дополнительной информации."
        )
        return

    systolic, diastolic = reading

    with db.get_session() as session:
        user_repo, measurement_repo = get_repositories(session)

        user = user_repo.get_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("Пожалуйста, используйте /start для регистрации.")
            return

        # Save measurement
        measurement = measurement_repo.create_measurement(
            user_id=user.id, systolic=systolic, diastolic=diastolic
        )

        # Check for daily measurement motivation
        today = date.today()
        daily_count = measurement_repo.get_daily_measurement_count(user.id, today)

        await message.answer(
            f"✅ Записано: {measurement.formatted_reading} mmHg"  # \n"
            # f"📅 Время: {measurement.measured_at.strftime('%Y-%m-%d %H:%M')}\n"
            # f"📊 Категория: {category}\n\n"
            # f"Используйте /report для загрузки данных."
        )

        # Send motivational message if user measured 3 times today
        if daily_count == 3:
            await message.answer("🎉 Спасибо, что измерили давление 3 раза за день!")


def get_bp_category(systolic: int, diastolic: int) -> str:
    """Get blood pressure category based on AHA guidelines."""
    if systolic <= 120 and diastolic <= 80:
        return "Нормальное"
    elif systolic <= 130 and diastolic <= 80:
        return "Повышенное"
    elif systolic <= 140 or diastolic <= 90:
        return "Высокое АД 1-й степени"
    elif systolic <= 180 or diastolic <= 120:
        return "Высокое АД 2-й степени"
    else:
        return "Гипертонический криз - обратитесь к врачу"
