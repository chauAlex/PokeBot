import discord
import asyncio
from discord.ext import commands
from Config import token
TOKEN = token
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

async def load():
    await bot.load_extension('Cogs')

asyncio.run(load())
bot.run(TOKEN)