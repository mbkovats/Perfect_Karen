import discord
from discord.ext import commands
from discord.utils import get
import os
from dotenv import load_dotenv
import random
import yt_dlp
import requests

load_dotenv()
BOT_TOKEN = os.getenv('TOKEN')
YT_TOKEN = os.getenv('YT_TOKEN')

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTION = {'format': 'bestaudio', 'noplaylist':'True'}
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
        
song_queue = []
repeat = 0
@client.command()
async def leave(ctx):
    global song_queue
    song_queue = []
    await ctx.guild.voice_client.disconnect()

@client.command()
async def noah(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice == None:
        await join(ctx)
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('16WheelTruck.mp3'))
    ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

def search(query):
    try: requests.get("".join(query))
    except: query = " ".join(query)
    else: query = "".join(query)
    with yt_dlp.YoutubeDL(YDL_OPTION) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
    return {'source': info['url'], 'title': info['title'], 'duration': info['duration']}

def link(query):
    try: requests.get("".join(query))
    except: query = " ".join(query)
    else: query = "".join(query)
    with yt_dlp.YoutubeDL(YDL_OPTION) as ydl:
        info = ydl.extract_info(query, download=False)
    return {'source': info['url'], 'title': info['title'], 'duration': info['duration']}

def search_first_playlist(query, YDL_OPTIONS):
    try: requests.get("".join(query))
    except: query = " ".join(query)
    else: query = "".join(query)
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(query, download=False)
    song_queue.append({'source': info['entries'][0]['url'], 'title': info['entries'][0]['title']})
    return {'source': info['entries'][0]['url'], 'title': info['entries'][0]['title'], 'duration': info['entries'][0]['duration']}

def search_playlist(query, YDL_OPTIONS):
    try: requests.get("".join(query))
    except: query = " ".join(query)
    else: query = "".join(query)
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(query, download=False)
    for i in range(info['playlist_count'] - 1):
        song_queue.append({'source': info['entries'][i]['url'], 'title': info['entries'][i]['title'], 'duration': info['entries'][i]['duration']})

def play_next(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if len(song_queue) > 1:
        if not repeat:
            del song_queue[0]
        voice.play(discord.FFmpegPCMAudio(song_queue[0]['source'], **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
        voice.is_playing()
    elif len(song_queue) == 1:
        del song_queue[0]
    
# def get_length(query):
#     try: requests.get("".join(query))
#     except: query = " ".join(query)
#     else: query = "".join(query)
#     with yt_dlp.YoutubeDL(YDL_OPTION) as ydl:
#         info = ydl.extract_info(query, download=False)
#     return info['playlist_count']

@client.command()
async def play(ctx, *query):
    channel = ctx.message.author.voice.channel
    if channel:
        voice = get(client.voice_clients, guild=ctx.guild)
        if query[0].find("playlist") != -1:
            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True', 'playlist_items': '1'}
            song = search_first_playlist(query, YDL_OPTIONS)
        elif query[0].find("https") != -1:
            song = link(query)
            song_queue.append(song)
        else:
            song = search(query)
            song_queue.append(song)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else: 
            voice = await channel.connect()
        if not voice.is_playing():
            voice.play(discord.FFmpegPCMAudio(song['source'], **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
            voice.is_playing()
            await ctx.send(f"`Now Playing: {song['title']} {song_queue[0]['duration']}`")
            if query[0].find("playlist") != -1:
                YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True', 'playliststart': '2'}
                search_playlist(query, YDL_OPTIONS)
        elif query[0].find("playlist") == -1:
            await ctx.send(f"`Added {song['title']} to queue`")
            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True', 'playlist_items': '1'}
            search_first_playlist(query, YDL_OPTIONS)
            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True', 'playliststart': '2'}
            search_playlist(query, YDL_OPTIONS)
    else:
        await ctx.send("You're not connected to any channel!")

@client.command()
async def queue(ctx):
    out = ""
    out += (f"`Playing: {song_queue[0]['title']} {song_queue[0]['duration']}`")
    for i in range(1,len(song_queue)):
        out = out + (f"`{i}. {song_queue[i]['title']} {song_queue[i]['duration']}`\n")
    await ctx.send(f"{out}")

@client.command()
async def shuffle(ctx):
    random.shuffle(song_queue)
    await ctx.send(f"`Shuffled!`")

@client.command()
async def skip(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    voice.pause()
    if song_queue[0]:
        await play_next(ctx)
        await ctx.send(f"`Now Playing: {song_queue[0]['title']} {song_queue[0]['duration']}`")
    else:
        await leave(ctx)

@client.command()
async def move(ctx, *query):
    song_queue[int(query[0])], song_queue[int(query[1])] = song_queue[int(query[1])], song_queue[int(query[0])]
    await ctx.send(f"`Moved {int(query[0])}. {song_queue[int(query[0])]['title']} to position {int(query[1])}`")

@client.command()
async def loop(ctx):
    global repeat
    repeat = repeat ^ 1
    await ctx.send("`Looped!`")

client.run(BOT_TOKEN)
