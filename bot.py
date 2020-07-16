import os

from discord.ext import commands
from dotenv import load_dotenv

from quote import get_quote

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='dm')
async def dm(ctx, to):
  if to == 'me':
    await greet(ctx.author)
  else:
    for user in ctx.message.mentions:
      await greet(user)

@bot.command(name='quote')
async def quote(ctx):
  q = get_quote()
  response = '> *{content}*\n> \n> {author}'.format(content=q['content'], author=q['author'])
  await ctx.send(response)

async def greet(user):
  response = 'Hi {mention}!'.format(mention=user.mention)
  await user.send(response)

bot.run(TOKEN)
