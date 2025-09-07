# Blood Pressure Tracker Bot

A Telegram bot for tracking blood pressure measurements with automated reminders and CSV report generation.

## Features

- **User Registration**: Automatic user registration when starting the bot
- **Blood Pressure Recording**: Parse and store measurements in format "120/80"
- **Automated Reminders**: Send daily reminders at configurable times (default: 7:00, 13:00, 20:00)
- **CSV Reports**: Generate comprehensive reports with statistics
- **Data Validation**: Validate blood pressure readings and classify by AHA guidelines
- **Database Support**: Uses SQLAlchemy for database flexibility (SQLite by default)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd blood-pressure-tracker
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your bot token from @BotFather
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# Required: Get from @BotFather on Telegram
TELEGRAM_TOKEN=your_bot_token_here

# Optional: Database URL (default: SQLite)
DATABASE_URL=sqlite:///blood_pressure.db

# Optional: Reminder times in 24-hour format
REMINDER_TIMES=07:00,13:00,20:00

# Optional: Debug mode
DEBUG=false
```

## Bot Commands

- `/start` - Register with the bot and see welcome message
- `/help` - Show help information
- `/report` - Generate and download CSV report
- Send blood pressure reading (e.g., "120/80") - Record measurement

## Development

### Running Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

### Linting

```bash
source .venv/bin/activate
ruff check src/ tests/
ruff format src/ tests/  # Auto-format code
```

### Project Structure

```
src/
├── bot/           # Telegram bot handlers
├── database/      # Database models and operations
├── services/      # Business logic (scheduler, reports)
└── config/        # Configuration management
tests/             # Unit tests
```

## Database

The bot uses SQLAlchemy for database operations, making it easy to switch between different database systems:

- **Development**: SQLite (default)
- **Production**: PostgreSQL, MySQL, or any SQLAlchemy-supported database

To change database, update the `DATABASE_URL` environment variable.

## Blood Pressure Categories

The bot classifies readings according to AHA guidelines:

- **Normal**: ≤120/≤80 mmHg
- **Elevated**: ≤130/≤80 mmHg
- **High BP Stage 1**: ≤140/≤90 mmHg
- **High BP Stage 2**: ≤180/≤120 mmHg
- **Hypertensive Crisis**: >180/>120 mmHg

## License

[License information here]