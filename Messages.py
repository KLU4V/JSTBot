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
roles = {'default': '', 'admin': '', 'available': []}


class JSTBotCL(discord.Client):
    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            logger.info(
                f'{self.user} подключились к чату:\n'
                f'{guild.name}(id: {guild.id})')

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(f'Привет, {member.name}!')
        await member.add_roles(discord.utils.get(member.guild.roles, name=roles['default']))

    async def on_message(self, message):
        global ban_words, roles

        checkable = True

        # roles checker sector start
        if not message:
            guild = message.guild
            channel_id = message.reference.channel_id
            channel = guild.get_channel(channel_id)
            if not channel:
                channel = await guild.fetch_channel(channel_id)

        member = message.author
        member_roles = [role.name for role in member.roles]

        if roles['admin'] in member_roles or roles['admin'] == '':
            # roles checker sector end

            # ban words sector start
            if message.content.startswith("$banwords add"):
                try:
                    ban_words.append(message.content.split('$banwords add ')[1])
                    await message.channel.send(
                        f'Successfully added a new ban word: ' + message.content.split('$banwords add ')[1])
                    checkable = False
                except Exception as e:
                    print(e)

            if message.content.startswith("$banwords multiply add"):
                try:
                    to_add = message.content.split('$banwords multiply add ')[1].split(' ')
                    for word in to_add:
                        ban_words.append(word)
                    await message.channel.send(
                        f'Successfully added new ban words')
                    checkable = False
                except Exception as e:
                    print(e)

            if message.content.startswith("$banwords remove"):
                try:
                    if message.content.split('$banwords remove ')[1] not in ban_words:
                        await message.channel.send('This word is not in banwords.')
                    else:
                        ban_words.pop(ban_words.index(message.content.split('$banwords remove ')[1]))
                        await message.channel.send(
                            'Successfully removed a ban word: ' + message.content.split("$banwords remove ")[1])
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

            if message.content.startswith("$banwords clear"):
                try:
                    ban_words.clear()
                except Exception as e:
                    print(e)
            # ban words sector end

            # roles sector start
            if message.content.startswith("$roles default set"):
                try:
                    roles['default'] = message.content.split("$roles default set ")[1]
                    await message.channel.send(f'Default role: ' + roles['default'])
                except Exception as e:
                    print(e)

            if message.content.startswith("$roles admin set"):
                try:
                    roles['admin'] = message.content.split("$roles admin set ")[1]
                    await message.channel.send(f'Admin role: ' + roles['admin'])
                except Exception as e:
                    print(e)

            if message.content.startswith("$roles list"):
                try:
                    await message.channel.send(roles)
                except Exception as e:
                    print(e)
            # roles sector end

        # check sector start
        if checkable is True:
            for ms in ban_words:
                if message.author == self.user:
                    return
                if ms in message.content.lower():
                    await message.delete()
                    await message.channel.send(f'Warning! Message includes banwords!')
        # check sector end


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = JSTBotCL(intents=intents)

client.run(settings['token'])
