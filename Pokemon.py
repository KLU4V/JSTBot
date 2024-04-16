import asyncio
import discord
from discord.ext import commands
import logging
from config import settings
import requests

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)


class JSTBotMusic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='exist', brief="Returns an existence of a pokemon")
    async def exist(self, ctx, name):
        try:
            poke = (f"https://pokeapi.co/api/v2/pokemon/{name.lower()}/")

            response = requests.get(poke)

            if response:
                await ctx.send(f'`🐽Этот покемон существует`')

            else:
                await ctx.send(f'`🐽Это не покемон, а что-то другое`')

        except Exception as e:
            await ctx.send(f'`🐽Это не покемон, а что-то другое`')

    @commands.command(name='abilities', brief="Returns abilities of a pokemon")
    async def abilities(self, ctx, name):
        try:
            poke = (f"https://pokeapi.co/api/v2/pokemon/{name.lower()}/")

            response = requests.get(poke)
            json_response = response.json()
            text = ''

            if response:
                for a in json_response['abilities']:
                    text += f'`🐽Name> {' '.join(str(a['ability']['name']).split('-'))}`\n'

                await ctx.send(text)

            else:
                await ctx.send(f'`🐽Это не покемон, а что-то другое`')

        except Exception as e:
            await ctx.send(f'`🐽Это не покемон, а что-то другое`')

    @commands.command(name='baseexp', brief="Returns base experience of a pokemon")
    async def baseexp(self, ctx, name):
        try:
            poke = (f"https://pokeapi.co/api/v2/pokemon/{name.lower()}/")

            response = requests.get(poke)
            json_response = response.json()

            if response:
                await ctx.send(f'`🐽У этого покемона {json_response['base_experience']} базового опыта`')

            else:
                await ctx.send(f'`🐽Это не покемон, а что-то другое`')

        except Exception as e:
            await ctx.send(f'`🐽Это не покемон, а что-то другое`')

    @commands.command(name='height', brief="Returns height of a pokemon")
    async def height(self, ctx, name):
        try:
            poke = (f"https://pokeapi.co/api/v2/pokemon/{name.lower()}/")

            response = requests.get(poke)
            json_response = response.json()

            if response:
                await ctx.send(f'`🐽Рост этого покемона - {int(json_response['height']) * 10} см`')

            else:
                await ctx.send(f'`🐽Это не покемон, а что-то другое`')

        except Exception as e:
            await ctx.send(f'`🐽Это не покемон, а что-то другое`')


async def main():
    await bot.add_cog(JSTBotMusic(bot))
    await bot.start(settings['token'])


asyncio.run(main())
