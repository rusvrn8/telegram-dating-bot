# Agent Guidelines for tg_bot

## Build/Test Commands

This is a Python Telegram bot project with no formal test framework or CI pipeline configured.

### Running the Bot
```bash
python my_bot.py           # Main dating bot (uses users_test.json)
python ruletka_bot.py      # Random chat bot
python test_bot.py         # Test bot for development
```

### Install Dependencies
```bash
pip install -r req.txt
```

### Running Tests
No test framework is currently configured. To add tests:
1. Install pytest: `pip install pytest pytest-asyncio`
2. Create test files following `test_*.py` pattern
3. Run specific test: `pytest tests/test_module.py -k test_function`
4. Run all tests: `pytest`

### Code Quality Tools (Not Currently Configured)
```bash
ruff check .                    # Linting
ruff format .                   # Formatting
ruff check --fix .             # Auto-fix linting issues
mypy my_bot.py                 # Type checking
```

## Code Style Guidelines

### Imports
- Standard library imports first (logging, json, os, random, threading)
- Third-party imports second (telegram, faker, cv2, numpy)
- Group related imports together
- Use absolute imports
- Example:
```python
import logging
import json
import os
import random
import threading

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters, ApplicationBuilder
from telegram.ext import CallbackContext
```

### Formatting
- 4 spaces for indentation (no tabs, except in ruletka_bot.py which uses tabs)
- UTF-8 encoding for JSON file operations
- Line length: keep reasonable, no strict limit
- Blank lines between top-level functions (2 lines)
- Blank lines between function sections (1 line)

### Types
- Minimal type hints used in existing code
- Add type hints where helpful, match existing style:
```python
async def start(update: Update, context: CallbackContext) -> None:
```
- User IDs are strings: `user_id = str(user_id)`
- Use explicit type conversion when needed

### Naming Conventions
- Functions: `snake_case` (e.g., `save_to_json`, `load_from_json`)
- Variables: `snake_case` (e.g., `users_file_path`, `filter_gender`)
- Constants: `CAPS_WITH_UNDERSCORES` (e.g., `SUPPORT_CHAT_ID`)
- Async handlers: descriptive names like `handle_matching_choice`

### Function Structure
- All bot handlers are async functions
- Function signatures: `async def function_name(update, context)` or `async def function_name(update: Update, context: CallbackContext)`
- Logging at function start: `logging.info('Function name...')`
- Return early in async handlers with multiple branches

### Error Handling
- Minimal error handling in current code
- Add try-except blocks for file I/O operations
- Context managers for file operations
- Thread-safe file access using locks:

```python
read_lock = threading.Lock()
write_lock = threading.Lock()

def save_to_json(data, file_path):
    with write_lock:
        with open(file_path, 'w', encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False)

def load_from_json(file_path):
    with read_lock:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)
            return data
        return {}
```

### Global Variables
- Module-level locks: `read_lock`, `write_lock`
- File paths as module constants: `users_file_path`
- Loaded data: `users`, `photos`, `likes`
- Job queue globals: `job_monitor`, `job_like`

### Bot Handler Patterns
- CommandHandler: `application.add_handler(CommandHandler('start', start))`
- CallbackQueryHandler: `application.add_handler(CallbackQueryHandler(register, pattern='^register$'))`
- MessageHandler: `application.add_handler(MessageHandler(filters.PHOTO, upload_photo))`
- Regex filters: `filters.Regex("^(Парень|Девушка)$")`

### Data Structures
- Users dict: nested dict with keys 'name', 'username', 'gender', 'age', 'goal', 'city', 'photo', 'seen'
- Photos dict: maps user_id to photo_file_id
- Likes dict: nested dict with 'likes' list and 'seen' list
- Use sets for filtering operations: `{u for u in users if ...}`

### String Formatting
- Use f-strings: `f'{user_id = }'`, `f"Имя: {random_user_data['name']}"`
- Russian text in bot responses with emojis where appropriate
- ensure_ascii=False in JSON dumps for Cyrillic support

### User Data Storage
- `context.user_data` for temporary session data (state machine)
- JSON files for persistent data (users_test.json, photos_test.json, likes_test.json)
- State machine pattern using `context.user_data['state']`
- Common states: 'name', 'gender', 'age', 'goal', 'city', 'filter', 'matching', 'exit'

### Key Files
- `my_bot.py` - Main dating bot with registration, likes, filters
- `ruletka_bot.py` - Random text chat bot (uses tabs)
- `test_bot.py` - Development test bot
- `req.txt` - Python dependencies
- `regions_rf.txt` - List of Russian regions

### When Adding Features
1. Make async functions for any bot interaction
2. Use type hints following existing patterns
3. Add logging.info at function start
4. Use existing `save_to_json` and `load_from_json` helpers
5. Add command handler in the `if __name__ == '__main__'` block
6. Update user_data state machine appropriately
7. Consider thread safety for any new file operations
