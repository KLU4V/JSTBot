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

    paused, duration, skipnumber, loop = False, 0, 0, 0
    queue, history = list(), list()
    current_song = {'name': None, 'duration': 0, 'link': None}

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
        await ctx.send('`hello`')

    @commands.command(name='connect', brief="Connects to the voice channel")
    async def connect(self, ctx):
        try:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
            self.voice_clients[ctx.guild.id] = voice_client
            await ctx.send("`JSTBot has connected to the voice channel.`")
        except Exception as e:
            print(e)

    @commands.command(name='disconnect', brief="Disconnects from the voice channel")
    async def disconnect(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].stop()
            await self.voice_clients[ctx.guild.id].disconnect()
            await ctx.send("`JSTBot has disconnected from the voice channel.`")
        except Exception as e:
            print(e)

    @commands.command(name='play', brief="Plays a single video or adds a video to the playlist, from a youtube URL")
    async def play(self, ctx, request):
        try:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
            self.voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            print(f'[play] {e}')

        try:
            if request[:5] == 'https' and 'playlist' in request:
                playlistVideos = Playlist.getVideos(request)

                for i in range(len(playlistVideos['videos'])):
                    self.queue.append(Video.getInfo(playlistVideos['videos'][i]['link'], mode=ResultMode.json)['link'])

                link = self.queue[0]

            elif request[:5] != 'https':
                song_info = CustomSearch(request, VideoSortOrder.relevance, limit=1)
                link = song_info.result()['result'][0]['link']

                self.queue.append(link)

            else:
                link = request

                self.queue.append(link)

            if not ctx.voice_client.is_playing():
                try:
                    link = self.queue[0]
                    song_info = Video.getInfo(link, mode=ResultMode.json)

                    self.current_song['name'] = song_info['title']
                    self.duration = int(song_info['duration']['secondsText'])
                    self.current_song['link'] = link
                    self.history.insert(0, self.current_song['link'])

                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(link, download=False))

                    song = data['url']
                    player = discord.FFmpegPCMAudio(song, **self.ffmpeg_options,
                                                    executable='C:/Path_Programms/ffmpeg.exe')
                    self.voice_clients[ctx.guild.id].play(player)

                    self.current_song['duration'] = time.strftime("%M:%S", time.gmtime(self.duration))
                    await ctx.send(f"`📀Playing> {self.current_song['name']}`\n`📀Duration> {self.current_song['duration']}`")

                except Exception as e:
                    print(f'[play_player] {e}')

            else:
                await ctx.send(f"`📀Queued> {link}`")

            while True:
                if self.paused is False and not ctx.voice_client.is_playing() and self.skipnumber == 0:
                    self.queue.pop(0)

                    try:
                        link = self.queue[0]
                        song_info = Video.getInfo(link, mode=ResultMode.json)

                        self.current_song['name'] = song_info['title']
                        self.duration = int(song_info['duration']['secondsText'])
                        self.current_song['link'] = link
                        self.history.insert(0, self.current_song['link'])

                        loop = asyncio.get_event_loop()
                        data = await loop.run_in_executor(None,
                                                          lambda: self.ytdl.extract_info(link, download=False))

                        song = data['url']
                        player = discord.FFmpegPCMAudio(song, **self.ffmpeg_options,
                                                        executable='C:/Path_Programms/ffmpeg.exe')
                        self.voice_clients[ctx.guild.id].play(player)

                        self.current_song['duration'] = time.strftime("%M:%S", time.gmtime(self.duration))
                        await ctx.send(
                            f"`📀Playing> {self.current_song['name']}`\n`📀Duration> {self.current_song['duration']}`")

                    except Exception as e:
                        print(f'[play_player] {e}')
                        break

                elif self.skipnumber >= 1:
                    try:
                        self.voice_clients[ctx.guild.id].stop()
                        await ctx.send(f"`📀Skipped> {self.current_song['name']}`")
                        for s in range(self.skipnumber - 1):
                            await ctx.send(f"`📀Skipped> {Video.getInfo(link, mode=ResultMode.json)['title']}`")
                            self.history.insert(0, link)
                            self.queue.pop(0)

                        self.skipnumber = 0

                    except Exception as e:
                        print(f'[play_skip] {e}')
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

            await ctx.send(f"`📀Paused> {self.current_song['name']}`")

        except Exception as e:
            print(f'[pause] {e}')

    @commands.command(name='resume', brief="Resumes a song")
    async def resume(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].resume()
            self.paused = False

            await ctx.send(f"`📀Resumed> {self.current_song['name']}`")

        except Exception as e:
            print(f'[resume] {e}')

    @commands.command(name='queue.clear', brief="Clears the playlist")
    async def queue_clear(self, ctx):
        try:
            self.queue.clear()
            self.paused = False

            await ctx.send("`Playlist has been cleared`")

        except Exception as e:
            print(f'[playlist_clear] {e}')

    @commands.command(name='queue.show', brief="Shows the playlist")
    async def queue_show(self, ctx):
        try:
            text = ""
            for s in self.queue:
                text += f'`📀{Video.getInfo(s, mode=ResultMode.json)['title']}`\n'
            await ctx.send(text)

        except Exception as e:
            print(f'[playlist_show] {e}')

    @commands.command(name='nowplaying', brief="Shows a current song")
    async def nowplaying(self, ctx):
        try:
            await ctx.send(f'`📀Playing> {self.current_song['name']}`\n`📀Duration> {self.current_song['duration']}`')

        except Exception as e:
            print(f'[nowplaying] {e}')

    @commands.command(name='stop', brief="Stops a song")
    async def stop(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].stop()
            self.queue.clear()
            self.paused = False

            await ctx.send("`Stopped`")
        except Exception as e:
            print(e)

    @commands.command(name='skipn', brief="Skips number of songs")
    async def skipn(self, ctx, n=1):
        try:
            self.skipnumber = n

        except Exception as e:
            print(f'[skip] {e}')

    @commands.command(name='skip', brief="Skips a single song")
    async def skip(self, ctx):
        try:
            self.skipnumber = 1

        except Exception as e:
            print(f'[skip] {e}')

    @commands.command(name='history', brief="Shows the history of songs")
    async def show_history(self, ctx):
        try:
            text = ""
            print(self.history)
            for s in self.history:
                text += f'`📀{Video.getInfo(s, mode=ResultMode.json)['title']}`\n'
            await ctx.send(text)

        except Exception as e:
            print(f'[history] {e}')

    @commands.command(name='loop', brief="Loops a song for a number of cycles")
    async def loop(self, ctx, n=1):
        try:
            self.loop = n

            for s in range(self.loop):
                self.queue.insert(1, self.current_song['link'])

                await ctx.send(f"`📀Looped for {n} times> {self.current_song['name']}`")

        except Exception as e:
            print(f'[loop] {e}')

    @commands.command(name='stoploop', brief="Stops a loop")
    async def stoploop(self, ctx):
        try:
            self.queue = self.queue[self.loop:]

            await ctx.send(f"`📀Stopped loop> {self.current_song['name']}`")

        except Exception as e:
            print(f'[stoploop] {e}')


async def main():
    await bot.add_cog(JSTBotMusic(bot))
    await bot.start(settings['token'])


asyncio.run(main())
