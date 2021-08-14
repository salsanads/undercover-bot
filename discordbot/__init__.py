from discordbot.bot import bot
from discordbot.cogs import *
from discordbot.handlers import *


def main(bot_token, bot_command_prefix=None):
    if bot_command_prefix is not None:
        bot.command_prefix = bot_command_prefix

    bot.run(bot_token)
