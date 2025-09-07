# Project Information

## Overview
Blood Pressure Tracker - A Telegram bot for blood pressure tracking and management.

## Tech Stack
- **Python 3.12** - Core language
- **SQLite** - Database for storing measurements
- **aiogram** - Telegram bot framework

## Core Functionality
- **Automated reminders**: Send reminders to registered users at 7:00, 13:00, 20:00
- **Data collection**: Receive and store blood pressure measurements with timestamps
- **Report generation**: Create and send CSV reports with measurements on demand

## Development Environment
- **Linting**: Use `ruff` for code formatting and linting
- **Type checking**: Follow type hints for better code quality
- **Testing**: Use `pytest` for unit tests (check for test runner setup)

## File Structure Guidelines
- Keep source code organized in logical modules
- Database models separate from business logic
- Bot handlers separate from data processing
- Configuration and environment variables in dedicated files

## Database Design
- Store measurements with timestamps
- User registration and management
- Reminder scheduling data

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

## Behavior configuration

### Reports

For each coding session:
1. Create a branch with a descriptive name that reflects what is going to be implemented
2. Create a .md file named as the created branch in the [reports](.claude/reports) folder.
Populate this file with a checklist plan and mark steps as completed with a short report on what was
done do complete it.

## Development principles
   
### KISS (Keep It Simple, Stupid)

Simplicity should be a key goal in design. Choose straightforward solutions over complex ones whenever possible. Simple solutions are easier to understand, maintain, and debug.

### YAGNI (You Aren't Gonna Need It)

Avoid building functionality on speculation. Implement features only when they are needed, not when you anticipate they might be useful in the future.

## Design Principles

- **Dependency Inversion**: High-level modules should not depend on low-level modules. Both should depend on abstractions.
- **Open/Closed Principle**: Software entities should be open for extension but closed for modification.
- **Single Responsibility**: Each function, class, and module should have one clear purpose.
- **Fail Fast**: Check for potential errors early and raise exceptions immediately when issues occur.

## Code Structure & Modularity

### File and Function Limits

- **Never create a file longer than 500 lines of code**. If approaching this limit, refactor by splitting into modules.
- **Functions should be under 50 lines** with a single, clear responsibility.
- **Classes should be under 100 lines** and represent a single concept or entity.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
- **Line length should be max 100 characters**.