import discord
import asyncio
import os
import logging
import yt_dlp
from discord.ext import commands
from config import settings

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

ban_words = list()


class JSTBotCL(discord.Client):
    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {'options': '-vn'}

    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            logger.info(
                f'{self.user} подключились к чату:\n'
                f'{guild.name}(id: {guild.id})')

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f'Привет, {member.name}!'
        )

    async def on_message(self, message):
        global ban_words

        checkable = True

        if message.content.startswith("$banwords add"):
            try:
                ban_words.append(message.content.split('$banwords add ')[1])
                checkable = False
            except Exception as e:
                print(e)

        if message.content.startswith("$banwords remove"):
            try:
                if message.content.split('$banwords remove ')[1] not in ban_words:
                    await message.channel.send('This word is not in banwords.')
                else:
                    ban_words.pop(ban_words.index(message.content.split('$banwords remove ')[1]))
                checkable = False
            except Exception as e:
                print(e)

        if message.content.startswith("$banwords list"):
            try:
                if bool(ban_words) is True:
                    await message.channel.send(str(ban_words).strip('[]'))
                else:
                    await message.channel.send('Empty')
                checkable = False
            except Exception as e:
                print(e)

        if checkable is True:
            for ms in ban_words:
                if message.author == self.user:
                    return
                if ms in message.content.lower():
                    await message.delete()
                    await message.channel.send(f'Warning! Message includes banwords!')


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = JSTBotCL(intents=intents)

client.run(settings['token'])
