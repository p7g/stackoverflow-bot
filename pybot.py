"""
Stackoverflow bot
"""
import html
import logging
import os
import aiohttp
from dotenv import load_dotenv
import discord
from discord.ext import commands

def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    BOT = commands.Bot(command_prefix=os.getenv('PREFIX', default='&'))
    LOG = logging.getLogger('PYBOT')
    SESSION = aiohttp.ClientSession()
    SEARCH = 'https://api.stackexchange.com/2.2/search/advanced'

    @BOT.command()
    async def ping(ctx):
        """
        Get the current latency of the bot
        """
        await ctx.send(f'{BOT.latency * 1000}ms')

    @BOT.command()
    async def halp(ctx, *message_parts):
        """
        Search for the given search term on StackOverflow
        """
        message = ' '.join(message_parts)

        LOG.info('Searching for "%s"', message)
        params = {
            'q': message,
            'sort': 'relevance',
            'order': 'desc',
            'site': 'stackoverflow',
            'filter': '!*1SgQGDMkNpCIzzMCq25IRX4u0u-1D8S2YxUITK_Q',
            'answers': 1,
            'pagesize': 1,
        }
        resp = await SESSION.get(SEARCH, params=params)
        data = await resp.json()

        if not data['items']:
            message = 'No results for "%s"!' % message
            LOG.info(message)
            return await ctx.send(message)

        item = data['items'][0]

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

    @BOT.event
    async def on_ready():
        """
        Log to the console when connected
        """
        LOG.info('Ready!!!!')

    BOT.run(os.getenv('TOKEN'))

if __name__ == '__main__':
    main()
