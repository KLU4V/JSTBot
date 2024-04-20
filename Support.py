from discord.ext import commands
import discord
import asyncio
import logging
import random
from config import settings

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)


class JSTBotHelp(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='support')
    async def support(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(color=discord.Color.yellow(), title='Справка для использования команд')
        embed.add_field(name="Команды информации", value=f"`$userinfo [участник]` - информация об участнике сервера\n"
                                                         f"`$serverinfo` - информация о сервере", inline=False)
        embed.add_field(name="Команды проигрывателя", value=f"`$connect` - подключение бота к голосовому каналу\n"
                                                         f"`$disconnect` - отключение бота из голосового канала\n"
                                                            f"`$play [ссылка]` - проигрывание отдельных видео или"
                                                            f" добавление"
                                                            f" видео в очередь с помощью ссылки YouTube\n"
                                                            f"`$pause` - остановка проигрывания трека\n"
                                                            f"`$resume` - воспроизведение проигрывания трека\n"
                                                            f"`$queue.clear` - очистка очереди\n"
                                                            f"`$queue.show` - показ очереди\n"
                                                            f"`$nowplaying` - показ играющего трека\n"
                                                            f"`$stop` - остановка проигрывания трека\n"
                                                            f"`$skipn [число]` -  пропуск нескольких треков\n"
                                                            f"`$skip` - пропуск играющего трека\n"
                                                            f"`$history` -  показ истории проигранных треков\n"
                                                            f"`$loop [число]` - создание цикла из песни на некоторое "
                                                            f"количество повторов\n"
                                                            f"`$stoploop` - остановка цикла\n"
                                                            f"`$remove [число]` - удаление трека из очереди по числу\n"
                                                            f"`$chillradio` - включение проигрывания Chill Radio\n"
                                                            f"`$synthwaveradio` - включение проигрывания"
                                                            f" Synthwave Radio\n"
                                                            f"`$phonkradio` - включение проигрывания Phonk Radio\n"
                                                            f"`$rockradio` - включение проигрывания Rock Radio",
                        inline=False)
        embed.add_field(name="Команды реакций", value=f"`$bite [участник]` - укусить участника\n"
                                                            f"`$kiss [участник]` - поцеловать участника\n"
                                                            f"`$hit [участник]` - ударить участника", inline=False)
        embed.add_field(name="Команды модерации", value=f"`$kick [участник]` - исключение участника\n"
                                                         f"`$ban [участник]` - блокировка участника\n"
                                                            f"`$banwords add [слово]` - добавление слова в "
                                                        f"список запрещенных\n"
                                                        f"`$banwords multiply add [слова]` - добавление нескольких слов"
                                                        f" в список запрещенных\n"
                                                        
                                                            f"`$banwords remove [слова]` - удаление слов из "
                                                        f"списка запрещенных\n"
                                                            f"`$banwords list` - просмотр списка запрещенных слов\n"
                                                            f"`$banwords clear` - очистка списка запрещенных слов\n"
                                                            f"`$roles default set [роль]` - установка роли для каждого "
                                                        f"участника\n"
                                                            f"`$roles admin set [роль]` - установка роли админа\n"
                                                            f"`$roles additional add [роль]` - добавление "
                                                        f"дополнительных"
                                                        f" ролей\n"
                                                        f"`$roles muted set` - установка роли для заглушенных\n"
                                                            f"`$roles list` -  список ролей\n"
                                                            f"`$mute [участник] [время]` - заглушить участника\n"
                                                            f"`$unmute [участник]` -  разглушить участника",
                        inline=False)
        embed.add_field(name="Команды покемонов", value=f"`$exists [покемон]` - проверка существования покемона\n"
                                                        f"`$baseexp [покемон]` - показ количества базового "
                                                        f"опыта покемона\n"
                                                        f"`$height [покемон]` - показ роста покемона", inline=False)
        await ctx.send(embed=embed)


async def main():
    await bot.add_cog(JSTBotHelp(bot))
    await bot.start(settings['token'])


asyncio.run(main())
