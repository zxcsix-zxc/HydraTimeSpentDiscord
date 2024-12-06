import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

class VoiceTimerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = True
        intents.guilds = True
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents,
        )

    async def setup_hook(self):
        await self.load_extension("cogs.voice_tracker")
        
    async def on_ready(self):
        print(f"Logged in as {self.user.name}")
        print(f"Bot is in {len(self.guilds)} guilds")
        
        # Check permissions in all guilds
        for guild in self.guilds:
            me = guild.me
            channel = guild.text_channels[0]  # Get first text channel
            permissions = channel.permissions_for(me)
            
            print(f"\nPermissions in {guild.name}:")
            print(f"Send Messages: {permissions.send_messages}")
            print(f"Embed Links: {permissions.embed_links}")
            print(f"Read Messages: {permissions.read_messages}")
            print(f"View Channel: {permissions.view_channel}")
            print(f"Connect Voice: {permissions.connect}")
            print(f"View Voice: {permissions.view_channel}")

    @commands.command(name='ping')
    async def ping(self, ctx):
        try:
            permissions = ctx.channel.permissions_for(ctx.guild.me)
            if not permissions.send_messages:
                return
            await ctx.send('Pong!')
        except Exception as e:
            print(f"Error in ping command: {e}")

def main():
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        raise ValueError("No token found in .env file")

    bot = VoiceTimerBot()
    bot.run(token)

if __name__ == "__main__":
    main() 