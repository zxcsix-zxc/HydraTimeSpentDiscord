# Discord Voice Timer Bot

A Discord bot that tracks and manages voice channel usage time for server members.

## Features

- Tracks time spent in voice channels for all server members
- Displays user voice time statistics and leaderboards
- Maintains persistent data across bot restarts
- Provides formatted time display in a human-readable format

## Commands

- `/ping` - Check if the bot is responsive
- `/show_leaderboard` - Display the top users by voice channel time
- `/show_profile [member]` - Show voice time statistics for a specific user or yourself

## Setup

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your Discord bot token:
- Create a `.env` file in the root directory
- Add your bot token: `DISCORD_TOKEN=your_token_here`

3. Run the bot:
```bash
python src/bot.py
```

## Project Structure

- `src/bot.py` - Main bot initialization and core functionality
- `src/cogs/voice_tracker.py` - Voice channel tracking and command implementations
- `src/database/db_manager.py` - Database operations for storing voice time data
- `src/utils/time_formatter.py` - Utility functions for time formatting

## Database

The bot uses SQLite to store voice time data persistently. The database automatically creates the necessary tables on first run.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.

---

Note: Make sure your bot has the necessary permissions in your Discord server:
- View Channels
- Read Messages/View Channels
- Send Messages
- Connect to Voice Channels
