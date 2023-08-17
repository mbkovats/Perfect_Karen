import discord
from discord.ext import commands
from discord.utils import get
import os
from dotenv import load_dotenv
import random
import yt_dlp
import time
import json

load_dotenv()
BOT_TOKEN = os.getenv('TOKEN')
YT_TOKEN = os.getenv('YT_TOKEN')

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix = '/', intents=intents)

players = {}

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
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice == None:
        await channel.connect()

@client.command()
async def leave(ctx):
    
    await ctx.guild.voice_client.disconnect()

@client.command()
async def noah(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice == None:
        await join(ctx)
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('16WheelTruck.mp3'))
    ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

@client.command()
async def play(ctx, url):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice == None:
        await join(ctx)
    ydl_opts = {'format': 'bestaudio'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    
    # OUTPUT_DIR = 'output'
    # if not os.path.exists(OUTPUT_DIR):
    #     os.mkdir(OUTPUT_DIR)
    # output_file = os.path.join(OUTPUT_DIR, f'run20.tsv')
    # print(f'Writing to {output_file}')
    # with open(output_file, 'w', encoding='utf-16') as f:
    #     f.write('...')
    # with open(output_file, 'a', encoding='utf-16') as f:
    #     new = json.dumps(info, indent = 4)
    #     f.write(new)
    # pepep = json.dumps(info, indent = 4)
    # print(pepep)
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    # print(info['playlist_index'])
    try:
        if info['_type'] == 'playlist':
            for video in range(info['playlist_count']):
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(info['entries'][video]['url'], **FFMPEG_OPTIONS)) 
    except:
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(info['url'], **FFMPEG_OPTIONS))
    ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
client.run(BOT_TOKEN)
