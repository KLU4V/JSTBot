import asyncio
import discord
from discord.ext import commands
import random, logging
from config import settings
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)
print(discord.__version__)


class JSTBotCM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='say_hello')
    async def say_helo(self, ctx):
        await ctx.send('hello')

    @commands.command(name='connect')
    async def connect(self, ctx):
        if not ctx.author.voice:
            await ctx.send("You are not connected to a voice channel.")
            return

        elif ctx.author.voice.channel.permissions_for(ctx.me).connect:
            channel = ctx.author.voice.channel
            vc = await channel.connect()

            await ctx.send(f"JSTBot has connected to {channel}")

        else:
            await ctx.send("JSTBot does not have the permission to join this voice channel.")

    @commands.command(name='disconnect')
    async def disconnect(self, ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

        if not voice_client:
            return await ctx.send("JSTBot is not connected to a voice channel.")

        await voice_client.disconnect()
        await ctx.send("JSTBot has disconnected from the voice channel.")

    @commands.command(brief="Plays a single video, from a youtube URL")
    async def play(self, ctx, url):
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        voice = voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

        if not voice.is_playing():
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']
            voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
            voice.is_playing()
        else:
            await ctx.send("Already playing song")
            return


async def main():
    await bot.add_cog(JSTBotCM(bot))
    await bot.start(settings['token'])


asyncio.run(main())
