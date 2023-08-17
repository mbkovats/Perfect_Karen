import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random

load_dotenv()
BOT_TOKEN = os.getenv('TOKEN')
YT_TOKEN = os.getenv('YT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix = '.', intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} is now running!')

@client.command()
async def coin(ctx):
    if random.randint(0,100)/100 >= 0.50:
        await ctx.send("`Heads`") 
    else:
        await ctx.send("`Tails`")

@client.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()

client.run(BOT_TOKEN)
