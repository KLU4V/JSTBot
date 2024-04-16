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
bite = ['https://media1.tenor.com/m/R_Oju0Tb-iUAAAAC/rip-bite.gif',
        'https://media1.tenor.com/m/krxP7bMkkEwAAAAd/baby-cute.gif',
        'https://media1.tenor.com/m/OHJt9nkDwkMAAAAd/dog-cat.gif',
        'https://media1.tenor.com/m/rEVPgJkCn9kAAAAd/gem-gemini.gif']
kiss = ['https://media1.tenor.com/m/9cEzDulFQ8kAAAAC/conybrown-conyandbrown.gif',
        'https://media1.tenor.com/m/aRNw3AI8GNoAAAAC/kiss-love.gif',
        'https://media1.tenor.com/m/o_5RQarGvJ0AAAAC/kiss.gif',
        'https://media1.tenor.com/m/WlyhX-h5wJ8AAAAC/kiss-kissing.gif']
hit = ['https://media1.tenor.com/m/6I9cJ0kdQXIAAAAC/this-is-the-way-tom-the-cat.gif',
       'https://media1.tenor.com/m/Lho_KrumiL4AAAAd/kevin-hasbu.gif',
       'https://media1.tenor.com/m/dO5uwvNfk2IAAAAd/penguin-hit-head.gif',
       'https://media1.tenor.com/m/lZ9MoOKHEtsAAAAd/cat-attack-hit-on-the-head.gif']


class JSTBotReactions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bite(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(color=discord.Color.yellow(), title=random.choice(["Ауч!", "Ай!"]))
        embed.description = f"{ctx.author.mention} укусил {member.mention}"
        url = (random.choice(bite))
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command()
    async def kiss(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(color=discord.Color.yellow(), title=':heart_eyes: :relaxed:')
        embed.description = f"{ctx.author.mention} поцеловал {member.mention}"
        url = (random.choice(kiss))
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command()
    async def hit(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(color=discord.Color.yellow(), title=random.choice(["Ауч!", "Ай!"]))
        embed.description = f"{ctx.author.mention} ударил {member.mention}"
        url = (random.choice(hit))
        embed.set_image(url=url)
        await ctx.send(embed=embed)




async def main():
    await bot.add_cog(JSTBotReactions(bot))
    await bot.start(settings['token'])


asyncio.run(main())
