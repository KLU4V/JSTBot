import asyncio
import discord
from discord.ext import commands
import logging
from config import settings
import random

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)


class JSTBotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='serverinfo')
    async def info(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        all = len(ctx.guild.members)
        members = len(list(filter(lambda m: not m.bot, ctx.guild.members)))
        bots = len(list(filter(lambda m: m.bot, ctx.guild.members)))
        channels = [len(list(filter(lambda m: str(m.type) == "text", ctx.guild.channels))),
                    len(list(filter(lambda m: str(m.type) == "voice", ctx.guild.channels)))]
        embed = discord.Embed(color=discord.Color.yellow(), title=f"Информация о сервере _{ctx.guild}_")
        embed.set_thumbnail(url=ctx.guild.icon)
        embed.add_field(name="Участники", value=f"Все: {all}\nЛюди: {members}\nБоты: {bots}")
        embed.add_field(name="Каналы",
                        value=f"Все: {channels[0] + channels[1]}\nТекстовые: {channels[0]}\nГолосовые: {channels[1]}")
        await ctx.send(embed=embed)

    @commands.command(name='userinfo')
    async def user(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        roles = [role for role in member.roles]
        embed = discord.Embed(color=discord.Color.yellow(), title=f"Информация об участнике _{member.name}_")
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name="Никнейм", value=member.display_name, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="", value='', inline=True)
        embed.add_field(name="Создал аккаунт", value=member.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=True)
        embed.add_field(name="Присоединился", value=member.joined_at.strftime("%d.%m.%Y %H:%M:%S"), inline=True)
        embed.add_field(name="", value='', inline=True)
        embed.add_field(name="Роли", value="\n".join(list(role.mention for role in roles)[1:]), inline=True)
        embed.add_field(name="Лучшая роль", value=member.top_role.mention, inline=True)
        await ctx.send(embed=embed)


async def main():
    await bot.add_cog(JSTBotInfo(bot))
    await bot.start(settings['token'])


asyncio.run(main())
