import asyncio
import discord
from discord.ext import commands
import logging
from config import settings
from discord.utils import get
from youtubesearchpython import *
from youtubesearchpython import VideosSearch
import time
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

    playlist, paused, duration, cur_name = list(), False, 0, None

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
            print(f'[play] {e}')

        try:
            if request[:5] != 'https':
                song_info = CustomSearch(request, VideoSortOrder.viewCount, limit=1)
                link = song_info.result()['result'][0]['link']

                self.playlist.append(link)

            elif request[:5] == 'https' and 'list' in request:
                playlistVideos = Playlist.getVideos(request)

                for i in range(len(playlistVideos['videos'])):
                    self.playlist.append(playlistVideos['videos'][i]['link'])

            else:
                link = request

                self.playlist.append(link)

            if len(self.playlist) == 1 and not ctx.voice_client.is_playing():
                link = self.playlist[0]
                song_info = Video.getInfo(link, mode=ResultMode.json)
                self.cur_name = song_info['title']

                self.duration = int(song_info['duration']['secondsText'])


                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(link, download=False))

                song = data['url']
                player = discord.FFmpegPCMAudio(song, **self.ffmpeg_options, executable='C:/Path_Programms/ffmpeg.exe')
                self.voice_clients[ctx.guild.id].play(player)

                convformat = time.strftime("%M:%S", time.gmtime(self.duration))
                await ctx.send(f":cd: Playing> {self.cur_name}\n{convformat}")

            else:
                await ctx.send(f":cd: Queued> {link}")

            while True:
                if self.paused is False and not ctx.voice_client.is_playing():
                    self.playlist.pop(0)

                    try:
                        link = self.playlist[0]
                        song_info = Video.getInfo(link, mode=ResultMode.json)
                        self.cur_name = song_info['title']
                        self.duration = int(song_info['duration']['secondsText'])

                        loop = asyncio.get_event_loop()
                        data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(link, download=False))

                        song = data['url']
                        player = discord.FFmpegPCMAudio(song, **self.ffmpeg_options,
                                                        executable='C:/Path_Programms/ffmpeg.exe')
                        self.voice_clients[ctx.guild.id].play(player)

                        convformat = time.strftime("%M:%S", time.gmtime(self.duration))
                        await ctx.send(f":cd: Playing> {self.cur_name}\n{convformat}")

                    except Exception as e:
                        print(f'[play] {e}')
                        break

                else:
                    await asyncio.sleep(1)

        except Exception as e:
            print(f'[play] {e}')

    @commands.command(name='pause', brief="Pauses a song")
    async def pause(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].pause()
            self.paused = True

            await ctx.send(f":cd: Paused> {self.cur_name}")

        except Exception as e:
            print(f'[pause] {e}')

    @commands.command(name='resume', brief="Resumes a song")
    async def resume(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].resume()
            self.paused = False

            await ctx.send(f":cd: Resumed> {self.cur_name}")

        except Exception as e:
            print(f'[resume] {e}')

    @commands.command(name='playlist.clear', brief="Clears the playlist")
    async def playlist_clear(self, ctx):
        try:
            self.playlist.clear()
            self.paused = False

            await ctx.send("Playlist has been cleared")

        except Exception as e:
            print(f'[playlist_clear] {e}')

    @commands.command(name='playlist.show', brief="Shows the playlist")
    async def playlist_show(self, ctx):
        try:
            await ctx.send(self.playlist)

        except Exception as e:
            print(f'[playlist_show] {e}')


async def main():
    await bot.add_cog(JSTBotMusic(bot))
    await bot.start(settings['token'])


asyncio.run(main())
