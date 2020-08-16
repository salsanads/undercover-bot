from collections.abc import Iterable

from discord.ext import commands
from discord.ext.commands import Bot, dm_only, guild_only

from quote import get_quote
from undercover import Status, controllers

from .errors import BotPlayerFound
from .helpers import CommandStatus, generate_mention, generate_message

bot = Bot(command_prefix="!")


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.send(generate_message(CommandStatus.GUILD_ONLY_COMMAND.name))
    elif isinstance(error, commands.errors.CommandInvokeError):
        if isinstance(error.original, BotPlayerFound):
            await ctx.send(
                generate_message(CommandStatus.HUMAN_PLAYER_ONLY.name)
            )
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.send(generate_message(CommandStatus.DM_ONLY_COMMAND.name))
    else:
        raise error


@bot.command(name="dm")
async def dm(ctx, to):
    if to == "me":
        await greet(ctx.author)
    else:
        for user in ctx.message.mentions:
            await greet(user)


@bot.command(name="quote")
async def quote(ctx):
    q = get_quote()
    reply = "> *{content}*\n> \n> {author}".format(
        content=q["content"], author=q["author"]
    )
    await ctx.send(reply)


@bot.command(name="start")
@guild_only()
async def start(ctx):
    channel_id = ctx.channel.id
    user_ids = retrieve_player_ids(ctx)
    game_states = controllers.start(channel_id, user_ids)
    for game_state in game_states:
        if game_state.status == Status.PLAYING_USER_FOUND:
            await send_mention_message(ctx, game_state, "playing_users")
        elif game_state.status == Status.PLAYED_WORD:
            await send_user_words_message(game_state)
        elif game_state.status == Status.PLAYING_ORDER:
            await send_mention_message(ctx, game_state, "playing_order")
        else:
            reply = generate_message(game_state.status.name, game_state.data)
            await ctx.send(reply)


@bot.command(name="eliminated")
@guild_only()
async def eliminate(ctx):
    game_states = controllers.eliminate(ctx.channel.id, ctx.author.id)
    for game_state in game_states:
        if game_state.status == Status.PLAYING_ORDER:
            await send_mention_message(ctx, game_state, "playing_order")
        elif game_state.status == Status.ASK_GUESSED_WORD:
            user = bot.get_user(ctx.author.id)
            reply = generate_message(game_state.status.name, game_state.data)
            await user.send(reply)
        else:
            reply = generate_message(game_state.status.name, game_state.data)
            await ctx.send(reply)


@bot.command(name="guess")
@dm_only()
async def guess(ctx):
    user_id = ctx.message.author.id
    word = str(ctx.message.content).strip()
    game_states = controllers.guess_word(user_id, word)
    for game_state in game_states:
        if game_state.status == Status.PLAYING_ORDER:
            channel = bot.get_channel(int(game_state.room_id))
            await send_mention_message(channel, game_state, "playing_order")
        elif game_state.status == Status.NOT_IN_GUESSING_TURN:
            reply = generate_message(game_state.status.name, game_state.data)
            await ctx.send(reply)
        else:
            channel = bot.get_channel(int(game_state.room_id))
            reply = generate_message(game_state.status.name, game_state.data)
            await channel.send(reply)


async def greet(user):
    response = "Hi {mention}!".format(mention=user.mention)
    await user.send(response)


def retrieve_player_ids(ctx):
    user_ids = {ctx.author.id}
    for user in ctx.message.mentions:
        if user.bot:
            raise BotPlayerFound
        user_ids.add(user.id)
    return list(user_ids)


async def send_user_words_message(game_state):
    user_words = game_state.data
    for user_id in user_words:
        message = generate_message(game_state.status.name, user_words[user_id])
        user = bot.get_user(user_id)
        await user.send(message)


async def send_mention_message(recipient, game_state, user_id_key):
    if isinstance(game_state.data[user_id_key], Iterable):
        mention = generate_mention(user_ids=game_state.data[user_id_key])
    else:
        mention = generate_mention(user_id=game_state.data[user_id_key])

    data = {user_id_key: mention}
    message = generate_message(game_state.status.name, data)
    await recipient.send(message)
