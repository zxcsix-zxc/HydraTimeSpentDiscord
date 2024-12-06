import aiosqlite
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path: str = "voice_time.db"):
        self.db_path = db_path
        # Only create the table if it doesn't exist
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Create the table if it doesn't exist, preserving existing data"""
        import sqlite3
        with sqlite3.connect(self.db_path) as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS user_voice_time (
                    user_id INTEGER,
                    guild_id INTEGER,
                    total_time INTEGER DEFAULT 0,
                    UNIQUE(user_id, guild_id)
                )
            """)
            db.commit()

    async def update_user_time(self, user_id: int, guild_id: int, session_time: int):
        async with aiosqlite.connect(self.db_path) as db:
            # Insert new record or update existing one
            await db.execute("""
                INSERT INTO user_voice_time (user_id, guild_id, total_time)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, guild_id)
                DO UPDATE SET total_time = total_time + ?
            """, (user_id, guild_id, session_time, session_time))
            await db.commit()

    async def get_leaderboard(self, guild_id: int, limit: int = 10):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT user_id, total_time 
                FROM user_voice_time 
                WHERE guild_id = ? 
                ORDER BY total_time DESC 
                LIMIT ?
            """, (guild_id, limit)) as cursor:
                return await cursor.fetchall()

    async def get_user_time(self, user_id: int, guild_id: int) -> int:
        """Get the total time for a specific user in a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT total_time 
                FROM user_voice_time 
                WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0

    async def reset_user_time(self, user_id: int, guild_id: int):
        """Reset time for a specific user in a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE user_voice_time 
                SET total_time = 0 
                WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            await db.commit()

    async def reset_guild_leaderboard(self, guild_id: int):
        """Reset all times for a specific guild"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                DELETE FROM user_voice_time 
                WHERE guild_id = ?
            """, (guild_id,))
            await db.commit()