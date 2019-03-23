"""
Stackoverflow bot
"""
import html
import logging
import os
from typing import Dict
import aiohttp
from dotenv import load_dotenv
import discord
from discord.ext import commands

def main():
    """ Start the bot """
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    bot: commands.Bot = commands.Bot(command_prefix=os.getenv('PREFIX', default='&'))
    log: logging.Logger = logging.getLogger('PYBOT')
    session: aiohttp.ClientSession = aiohttp.ClientSession()
    search: str = 'https://api.stackexchange.com/2.2/search/advanced'

    @bot.command()
    async def ping(ctx):
        """
        Get the current latency of the bot
        """
        await ctx.send(f'{bot.latency * 1000}ms')

    @bot.command()
    async def halp(ctx, *message_parts: str):
        """
        Search for the given search term on StackOverflow
        """
        message: str = ' '.join(message_parts)

        log.info('Searching for "%s"', message)
        params = {
            'q': message,
            'sort': 'relevance',
            'order': 'desc',
            'site': 'stackoverflow',
            'filter': '!*1SgQGDMkNpCIzzMCq25IRX4u0u-1D8S2YxUITK_Q',
            'answers': 1,
            'pagesize': 1,
        }
        resp = await session.get(search, params=params)
        data = await resp.json()

        if not data['items']:
            message = 'No results for "%s"!' % message
            log.info(message)
            return await ctx.send(message)

        item: Dict = data['items'][0]

        description = (
            html.unescape(item['body_markdown'])
            + '\n\n**Answer:**\n'
            + html.unescape(item['answers'][0]['body_markdown'])
        )

        embed = discord.Embed(
            title=html.unescape(item['title']),
            url=item['link'],
            description=(
                (description[:2045]
                 + '...')
                if len(description) > 2048
                else description
            ),
        )
        await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        """
        Log to the console when connected
        """
        log.info('Ready!!!!')

    bot.run(os.getenv('TOKEN'))

if __name__ == '__main__':
    main()
