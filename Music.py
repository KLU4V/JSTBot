import asyncio
import discord
from discord.ext import commands
import random, logging
from config import settings
from discord.utils import get
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

    ffmpeg_options = {'options': '-vn'}

    def __init__(self, bot):
        self.bot = bot

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
    async def play(self, ctx, url):
        try:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
            self.voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            print(e)

        try:

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegPCMAudio(song, **self.ffmpeg_options, executable='C:/Path_Programms/ffmpeg.exe')

            self.voice_clients[ctx.guild.id].play(player)
            await ctx.send("Playing")

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
            await ctx.send("Stopping ")

        except Exception as e:
            print(e)


async def main():
    await bot.add_cog(JSTBotMusic(bot))
    await bot.start(settings['token'])


asyncio.run(main())
