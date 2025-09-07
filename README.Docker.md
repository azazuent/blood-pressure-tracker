# Docker Setup for Blood Pressure Tracker

## Prerequisites

- Docker and Docker Compose installed
- Telegram Bot Token (get from @BotFather)

## Quick Start

1. **Clone the repository** (if not already done)

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your Telegram bot token
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Check logs:**
   ```bash
   docker-compose logs -f blood-pressure-bot
   ```

## Configuration

### Environment Variables

Set these in your `.env` file:

- `TELEGRAM_TOKEN` - Your Telegram bot token (required)
- `DATABASE_URL` - Database connection string (default: SQLite in volume)
- `REMINDER_TIMES` - Reminder times in MSK timezone (default: 07:00,13:00,20:00)
- `DEBUG` - Debug mode (default: false)

### Data Persistence

The application uses Docker volumes for data persistence:

- `blood_pressure_data` - SQLite database storage
- `blood_pressure_logs` - Application logs

## Management Commands

### Start the bot
```bash
docker-compose up -d
```

### Stop the bot
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### Restart the bot
```bash
docker-compose restart
```

### Update the bot
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup database
```bash
docker cp blood-pressure-tracker:/app/data/blood_pressure.db ./backup.db
```

### Restore database
```bash
docker cp ./backup.db blood-pressure-tracker:/app/data/blood_pressure.db
docker-compose restart
```

## Troubleshooting

### Check container status
```bash
docker-compose ps
```

### Check container health
```bash
docker inspect blood-pressure-tracker --format='{{.State.Health.Status}}'
```

### Access container shell
```bash
docker-compose exec blood-pressure-bot sh
```

### Remove all data (careful!)
```bash
docker-compose down -v
```

## Production Considerations

1. **Security**: The container runs as non-root user
2. **Logging**: Logs are rotated (max 10MB, 3 files)
3. **Health checks**: Container includes health monitoring
4. **Restart policy**: Automatically restarts unless stopped
5. **Timezone**: Reminders are sent in MSK (UTC+3) timezone

## Network

The bot creates its own network (`blood_pressure_network`) for isolation.