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

ban_words = []
roles = {'default': '', 'admin': '', 'additional': []}
welcome_message = f'Привет!'


class JSTBotCL(discord.Client):
    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)
    warns = {}
    msgs = {}

    ffmpeg_options = {'options': '-vn'}

    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            logger.info(
                f'{self.user} подключились к чату:\n'
                f'{guild.name}(id: {guild.id})')

    async def on_member_join(self, member):
        global welcome_message

        await member.create_dm()
        await member.dm_channel.send(welcome_message)
        try:
            await member.add_roles(discord.utils.get(member.guild.roles, name=roles['default']))
        except Exception as e:
            print(e)

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
            if message.content.startswith("$help"):
                try:
                    await message.channel.send("Kаждая команда вводится в формате $command:")
                    await message.channel.send(
                        "```Kоманда $help выводит список всех доступных команд, и за что они отвечают```")
                    await message.channel.send(
                        "```Kоманда $kick выгоняет указанного пользователя с сервера, формат ввода: $kick @username```")
                    await message.channel.send(
                        "```Kоманда $ban банит пользователя на сервере и кикает его, формат ввода: $ban @username```")
                    await message.channel.send(
                        "```Kоманда $banwords add добавляет слово в список запрещённых слов на сервере,"
                        " формат ввода: $banwords add word```")
                    await message.channel.send(
                        "```Kоманда $banwords multiply add может добавить несколько слов, формат ввода:"
                        " $banwords multiply add words (слова через пробел)```")
                    await message.channel.send(
                        "```Kоманда $banwords remove удаляет слово из списка запрещённых, формат ввода:"
                        " $banwords add word```")
                    await message.channel.send("```Kоманда $banwords list выводит список запрещённых слов```")
                    await message.channel.send("```Kоманда $banwords clear очищает список запрещённых слов```")
                    await message.channel.send(
                        "```Kоманда $roles default set добавляет роль по умолчанию, формат ввода:"
                        " $roles default set role```")
                    await message.channel.send(
                        "```Kоманда $roles admin set добавляет роль админа, который имеет разрешение"
                        " использовать команды,"
                        " формат ввода: $roles admin set role```")
                    await message.channel.send(
                        "```Kоманда $roles additional add добавляет дополнительную роль,"
                        " формат ввода: $roles additional add role```")
                    await message.channel.send("```Kоманда $roles list выводит список ролей```")
                    await message.channel.send(
                        "```Kоманда $mute выдаёт пользователю мут на определённое время, "
                        "формат ввода: $mute @username time (в минутах)```")
                    await message.channel.send(
                        "```Kоманда $unmute выдаёт пользователю мут на определённое время,"
                        " формат ввода: $unmute @username```")
                    await message.channel.send(
                        "```Kоманда $muted list выводит список пользователей которым дали мут```")
                    await message.channel.send("Вот список всех доступных команд. Большинство команд может вводить "
                                               "только админ, поэтому, перед использованием бота, рекомендуется указать"
                                               " админа с помощью команды $roles admin set role, роль заменить на роль,"
                                               " которую необходимо назначить админом")
                except Exception as e:
                    print(e)

            # ban words sector start
            if message.content.startswith("$kick "):
                if roles['admin'] in member_roles:
                    try:
                        # Getting a user mention for a kick
                        user_to_kick = message.mentions[0]
                        await user_to_kick.kick(reason="Requested by moderator")
                        await message.channel.send(f"{user_to_kick.name} was kicked from the server")
                    except IndexError:
                        await message.channel.send("The user was not mentioned for the kick")
                else:
                    await message.channel.send("You do not have permission to use this command")
            if message.content.startswith("$ban "):
                if roles['admin'] in member_roles:
                    try:
                        # Getting a user mention for a ban
                        user_to_ban = message.mentions[0]
                        await user_to_ban.ban(reason="Requested by moderator")
                        await message.channel.send(f"{user_to_ban.name} was banned from the server")
                    except IndexError:
                        await message.channel.send("The user was not mentioned for the ban")
                else:
                    await message.channel.send("You do not have permission to use this command")
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
                    guild = message.guild
                    server_roles = [role.name for role in guild.roles]

                    roles['default'] = message.content.split("$roles default set ")[1]
                    if roles['default'] in server_roles:
                        await message.channel.send(f'Default role: ' + roles['default'])
                    else:
                        roles['default'] = ''
                        await message.channel.send('This role does not exist')
                except Exception as e:
                    print(e)

            if message.content.startswith("$roles admin set"):
                try:
                    guild = message.guild
                    server_roles = [role.name for role in guild.roles]

                    roles['admin'] = message.content.split("$roles admin set ")[1]
                    if roles['admin'] in server_roles:
                        await message.channel.send(f'Admin role: ' + roles['admin'])
                    else:
                        roles['admin'] = ''
                        await message.channel.send('This role does not exist')
                except Exception as e:
                    print(e)

            if message.content.startswith("$roles additional add"):
                try:
                    guild = message.guild
                    server_roles = [role.name for role in guild.roles]

                    roles['additional'].append(message.content.split("$roles additional add ")[1])
                    if message.content.split("$roles additional add ")[1] in server_roles:
                        await message.channel.send(
                            f'Added an additional role: ' + message.content.split("$roles additional add ")[1])
                    else:
                        roles['additional'].pop(-1)
                        await message.channel.send('This role does not exist')
                except Exception as e:
                    print(e)

            if message.content.startswith("$roles list"):
                try:
                    await message.channel.send(roles)
                except Exception as e:
                    print(e)
            # roles sector end

            # mute command
            if message.content.startswith("$mute"):
                if roles['admin'] in member_roles:
                    try:
                        user_to_mute = message.mentions[0]
                        time_in_minutes = int(message.content.split("$mute ")[-1].split()[-1])

                        # Check if the user is already muted
                        muted_role = discord.utils.get(message.guild.roles, name="Muted")
                        if muted_role in user_to_mute.roles:
                            await message.channel.send("This user is already muted")
                            return

                        # Create Muted role if it doesn't exist
                        if muted_role is None:
                            muted_role = await message.guild.create_role(name="Muted")

                        await user_to_mute.add_roles(muted_role)
                        await message.channel.send(
                            f'{user_to_mute} was muted for {time_in_minutes} minutes')
                        await message.channel.set_permissions(user_to_mute, send_messages=False)
                        await asyncio.sleep(time_in_minutes * 60)
                        await message.channel.set_permissions(user_to_mute, send_messages=True)
                        await user_to_mute.remove_roles(muted_role)  # Remove the Muted role after the mute duration
                    except Exception as e:
                        print(e)
            # unmute command
            if message.content.startswith("$unmute"):
                if roles['admin'] in member_roles:
                    try:
                        user_to_unmute = message.mentions[0]
                        muted_role = discord.utils.get(message.guild.roles, name="Muted")

                        if muted_role not in user_to_unmute.roles:
                            await message.channel.send("This user is not muted")
                            return

                        await message.channel.set_permissions(user_to_unmute, send_messages=True)
                        await user_to_unmute.remove_roles(muted_role)
                        await message.channel.send(f'{user_to_unmute} has been unmuted')
                    except Exception as e:
                        print(e)
            if message.content.startswith("$muted list"):
                try:
                    muted_role = discord.utils.get(message.guild.roles, name="Muted")
                    muted_members = [member.display_name for member in message.guild.members if
                                     muted_role in member.roles]
                    if muted_members:
                        await message.channel.send("Users with Muted role: " + ', '.join(muted_members))
                    else:
                        await message.channel.send("Empty")
                except Exception as e:
                    print(e)
        # here
        if '$' not in message.content:
            try:
                if message.author == self.user:
                    return
                mess = self.msgs.get(message.author.id, 0)
                mess += 1
                if mess % 20 == 0 and mess >= 20:
                    user_to_lvl = message.author
                    lvl = discord.utils.get(message.guild.roles, name=f"level {mess // 20}")
                    if lvl is None:
                        lvl = await message.guild.create_role(name=f"level {mess // 20}")
                    await user_to_lvl.add_roles(lvl)
                    await message.channel.send(
                        f'{user_to_lvl} receives a level {mess // 20} role for being active'
                        f' and sending {mess} messages')
                self.msgs[message.author.id] = mess
            except Exception as e:
                print(e)
        # check sector start
        if checkable is True:
            for ms in ban_words:
                if message.author == self.user:
                    return
                if ms in message.content.lower():
                    warnings = self.warns.get(message.author.id, 0)
                    if warnings == 3:
                        warnings = 0
                    warnings += 1
                    self.warns[message.author.id] = warnings
                    if warnings == 3:
                        user_to_mute = message.author
                        muted_role = discord.utils.get(message.guild.roles, name="Muted")
                        await user_to_mute.add_roles(muted_role)
                        await message.channel.send(
                            f'Warning! Message includes a banned word! {user_to_mute} was muted for 5 minutes')
                        await message.channel.set_permissions(user_to_mute, send_messages=False)
                        await message.delete()
                        await asyncio.sleep(300)
                        await message.channel.set_permissions(user_to_mute, send_messages=True)
                        await user_to_mute.remove_roles(muted_role)  # Remove the Muted role after the mute duration
                        del self.warns[message.author.id]
                    else:
                        await message.delete()
                        await message.channel.send(f'Warning! Message includes a banned word! Warning {warnings}/3')
        # check sector end


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = JSTBotCL(intents=intents)

client.run(settings['token'])
