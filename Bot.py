import discord
import asyncio
import logging
from discord.ext import commands
from config import settings

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

ban_words = ['something']


class JSTBotCL(discord.Client):

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
