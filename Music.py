import asyncio
import discord
from discord.ext import commands
import logging
from config import settings
from discord.utils import get
from youtubesearchpython import *
from youtubesearchpython import VideosSearch
import yt_dlp

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'default_search': 'auto',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

print(discord.__version__)


class JSTBotMusic(commands.Cog):
    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {'before_options': '-reconnect 1',
                      'options': '-vn'}
    playlist = list()

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if not member.id == self.bot.user.id:
            return

        elif before.channel is None:
            voice = after.channel.guild.voice_client
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time == 300:
                    await voice.disconnect()
                if not voice.is_connected():
                    break

    @commands.command(name='say_hello')
    async def say_helo(self, ctx):
        await ctx.send('hello')

    @commands.command(name='connect', brief="Connects to the voice channel")
    async def connect(self, ctx):
        try:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
            self.voice_clients[ctx.guild.id] = voice_client
            await ctx.send("JSTBot has connected to the voice channel.")
        except Exception as e:
            print(e)

    @commands.command(name='disconnect', brief="Disconnects from the voice channel")
    async def disconnect(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].stop()
            await self.voice_clients[ctx.guild.id].disconnect()
            await ctx.send("JSTBot has disconnected from the voice channel.")
        except Exception as e:
            print(e)

    @commands.command(name='play', brief="Plays a single video, from a youtube URL")
    async def play(self, ctx, request):
        try:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
            self.voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            print(e)

        try:
            if request[:5] != 'https':
                song_info = CustomSearch(request, VideoSortOrder.viewCount, limit=1)
                link = song_info.result()['result'][0]['link']
                name = song_info.result()['result'][0]['title']
                duration = song_info.result()['result'][0]['accessibility']['duration']

            else:
                song_info = Video.getInfo(request, mode=ResultMode.json)
                link = request
                name = song_info['result'][0]['title']
                duration = song_info['result'][0]['accessibility']['duration']

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(link, download=False))

            song = data['url']
            player = discord.FFmpegPCMAudio(song, **self.ffmpeg_options, executable='C:/Path_Programms/ffmpeg.exe')

            self.voice_clients[ctx.guild.id].play(player)
            await ctx.send(f"Playing {name}\nDuration: {duration}")

        except Exception as e:
            print(e)

    @commands.command(name='pause', brief="Pauses a song")
    async def pause(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].pause()
            await ctx.send("Pausing")

        except Exception as e:
            print(e)

    @commands.command(name='resume', brief="Resumes a song")
    async def resume(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].resume()
            await ctx.send("Resuming")

        except Exception as e:
            print(e)

    @commands.command(name='stop', brief="Resumes a song")
    async def stop(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].stop()
            self.playlist.clear()
            await ctx.send("Stopping ")

        except Exception as e:
            print(e)

    @commands.command(name='play clear', brief="Clears the playlist")
    async def play_clear(self, ctx):
        try:
            self.playlist.clear()

            await ctx.send("Stopping ")

        except Exception as e:
            print(e)


async def main():
    await bot.add_cog(JSTBotMusic(bot))
    await bot.start(settings['token'])


asyncio.run(main())
