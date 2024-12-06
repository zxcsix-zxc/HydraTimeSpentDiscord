from datetime import datetime
import discord
from discord.ext import commands
from database.db_manager import DatabaseManager
from utils.time_formatter import format_duration

class VoiceTracker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = DatabaseManager()
        self.user_sessions = {}
        print("VoiceTracker cog initialized!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            user_key = (member.id, member.guild.id)
            
            if before.channel is None and after.channel is not None:
                self.user_sessions[user_key] = datetime.now()
            
            elif before.channel is not None and after.channel is None:
                start_time = self.user_sessions.pop(user_key, None)
                if start_time:
                    duration = int((datetime.now() - start_time).total_seconds())
                    await self.db.update_user_time(member.id, member.guild.id, duration)
            
            elif before.channel != after.channel:
                start_time = self.user_sessions.get(user_key)
                if start_time:
                    duration = int((datetime.now() - start_time).total_seconds())
                    await self.db.update_user_time(member.id, member.guild.id, duration)
                    self.user_sessions[user_key] = datetime.now()

        except Exception as e:
            print(f"Error in voice state update: {str(e)}")

    @commands.command(name="leaderboard", aliases=["lb"])
    async def show_leaderboard(self, ctx):
        """Shows top 5 users in voice chat time"""
        try:
            await self._update_current_sessions(ctx.guild)
            leaderboard_data = await self.db.get_leaderboard(ctx.guild.id, limit=5)
            
            embed = discord.Embed(
                title="🏆 Top 5 Voice Champions",
                description="Most active voice chat users",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )

            # Add trophy emojis for top 3
            trophies = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

            if not leaderboard_data:
                embed.description = "No voice activity recorded yet!"
            else:
                for rank, (user_id, total_time) in enumerate(leaderboard_data):
                    user = ctx.guild.get_member(user_id)
                    if user:
                        formatted_time = format_duration(total_time)
                        embed.add_field(
                            name=f"{trophies[rank]} {user.display_name}",
                            value=f"Time: **{formatted_time}**",
                            inline=False
                        )

            embed.set_footer(text=f"Server: {ctx.guild.name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Error in leaderboard command: {str(e)}")
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.command(name="profile", aliases=["p"])
    async def show_profile(self, ctx, member: discord.Member = None):
        """Shows voice chat statistics for a user"""
        try:
            member = member or ctx.author
            await self._update_current_sessions(ctx.guild)
            
            # Get user's total time
            total_time = await self.db.get_user_time(member.id, ctx.guild.id)
            
            # Get user's rank
            leaderboard_data = await self.db.get_leaderboard(ctx.guild.id)
            user_rank = next((rank + 1 for rank, (uid, _) in enumerate(leaderboard_data) 
                            if uid == member.id), len(leaderboard_data) + 1)

            embed = discord.Embed(
                title="🎮 Voice Profile",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            # Set user's avatar as thumbnail
            embed.set_thumbnail(url=member.display_avatar.url)

            # Add user info
            embed.add_field(
                name="👤 User",
                value=f"**{member.display_name}**",
                inline=False
            )

            # Add time spent
            formatted_time = format_duration(total_time)
            embed.add_field(
                name="⏱️ Total Time in Voice",
                value=f"**{formatted_time}**",
                inline=True
            )

            # Add rank
            rank_emoji = "👑" if user_rank == 1 else "🏅"
            embed.add_field(
                name=f"{rank_emoji} Server Rank",
                value=f"**#{user_rank}**",
                inline=True
            )

            # Add join date
            joined_at = member.joined_at.strftime("%B %d, %Y") if member.joined_at else "Unknown"
            embed.add_field(
                name="📅 Joined Server",
                value=joined_at,
                inline=True
            )

            # Add status indicator
            if member.voice:
                embed.add_field(
                    name="📡 Current Status",
                    value="🟢 In Voice Channel",
                    inline=True
                )
            else:
                embed.add_field(
                    name="📡 Current Status",
                    value="⚫ Not in Voice",
                    inline=True
                )

            embed.set_footer(text=f"Server: {ctx.guild.name}")
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"Error in profile command: {str(e)}")
            await ctx.send(f"An error occurred: {str(e)}")

    async def _update_current_sessions(self, guild):
        """Update time for users currently in voice channels"""
        try:
            for voice_channel in guild.voice_channels:
                for member in voice_channel.members:
                    user_key = (member.id, guild.id)
                    start_time = self.user_sessions.get(user_key)
                    if start_time:
                        duration = int((datetime.now() - start_time).total_seconds())
                        await self.db.update_user_time(member.id, guild.id, duration)
                        self.user_sessions[user_key] = datetime.now()
        except Exception as e:
            print(f"Error updating current sessions: {str(e)}")

async def setup(bot):
    await bot.add_cog(VoiceTracker(bot)) 