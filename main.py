import discord
from discord.ext import commands
from discord.utils import get
import os
from dotenv import load_dotenv
import random
import yt_dlp
import time
import json
import requests
import copy

load_dotenv()
BOT_TOKEN = os.getenv('TOKEN')
YT_TOKEN = os.getenv('YT_TOKEN')

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
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

# @client.command()
# async def play(ctx, url):
#     voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
#     if voice == None:
#         await join(ctx)
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url, download=False)
    
#     # OUTPUT_DIR = 'output'
#     # if not os.path.exists(OUTPUT_DIR):
#     #     os.mkdir(OUTPUT_DIR)
#     # output_file = os.path.join(OUTPUT_DIR, f'run20.tsv')
#     # print(f'Writing to {output_file}')
#     # with open(output_file, 'w', encoding='utf-16') as f:
#     #     f.write('...')
#     # with open(output_file, 'a', encoding='utf-16') as f:
#     #     new = json.dumps(info, indent = 4)
#     #     f.write(new)
#     # pepep = json.dumps(info, indent = 4)
#     # print(pepep)
#     voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
#     # print(info['playlist_index'])
#     # try:
#     #     if info['_type'] == 'playlist':
#     for video in range(info['playlist_count']):
#         source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(info['entries'][video]['url'], **FFMPEG_OPTIONS)) 
#         ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
#         # start = time.time()
#         # while time.time() < start + 11:
#         #     pass
#         #     print('hit1')
#         print('hit2')
song_queue = []
#Search videos from key-words or links
def search(arg):
    try: requests.get("".join(arg))
    except: arg = " ".join(arg)
    else: arg = "".join(arg)
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        
    return {'source': info['url'], 'title': info['title']}

def search_playlist(arg):
    try: requests.get("".join(arg))
    except: arg = " ".join(arg)
    else: arg = "".join(arg)
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(arg, download=False)
    song_queue.append({'source': info['entries'][0]['url'], 'title': info['entries'][0]['title']})
    for i in range(1,info['playlist_count']):
        song_queue.append({'source': info['entries'][i]['url'], 'title': info['entries'][i]['title']})
    return {'source': info['entries'][0]['url'], 'title': info['entries'][0]['title']}

#Plays the next song in the queue
async def play_next(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if len(song_queue) > 1:
        del song_queue[0]
        voice.play(discord.FFmpegPCMAudio(song_queue[0]['source'], **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
        voice.is_playing()
        await ctx.send(f"`Now Playing: {song_queue[0]['title']}`")

def get_length(arg):
    try: requests.get("".join(arg))
    except: arg = " ".join(arg)
    else: arg = "".join(arg)
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(arg, download=False)
    return info['playlist_count']

@client.command()
async def play(ctx, *arg):
    channel = ctx.message.author.voice.channel

    if channel:
        voice = get(client.voice_clients, guild=ctx.guild)
        if arg[0].find("playlist") == -1:
            song = search(arg)
            song_queue.append(song)
        else:
            song = search_playlist(arg)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else: 
            voice = await channel.connect()
        if not voice.is_playing():
            voice.play(discord.FFmpegPCMAudio(song['source'], **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
            voice.is_playing()
            await ctx.send(f"`Now Playing: {song['title']}`")
        elif arg[0].find("playlist") == -1:
            await ctx.send("Added to queue")
    else:
        await ctx.send("You're not connected to any channel!")

@client.command()
async def queue(ctx):
    for i in range(len(song_queue)):
        await ctx.send(f"`{i + 1}. {song_queue[i]['title']}`")

@client.command()
async def shuffle(ctx):
    random.shuffle(song_queue)
    await ctx.send(f"`Shuffled!`")

@client.command()
async def skip(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    voice.pause()
    await play_next(ctx)

client.run(BOT_TOKEN)
