
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os


load_dotenv()
class MyBot(commands.Bot):
    async def setup_hook(self):
        # load every cog in the cogs/ folder automatically
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
        await self.tree.sync()  

intents = discord.Intents.default()
intents.message_content = True
bot = MyBot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
   


bot.run(os.environ["DISCORD_TOKEN"])