from discord.ext import commands
from discord.ext.commands import Bot, guild_only

from quote import get_quote
from undercover import Status, controllers

from .helpers import CommandStatus, generate_mentions, generate_message

bot = Bot(command_prefix="!")


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.send(generate_message(CommandStatus.GUILD_ONLY_COMMAND.name))
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
    user_ids = {ctx.author.id}
    for user in ctx.message.mentions:
        user_ids.add(user.id)
    game_states = controllers.start(channel_id, list(user_ids))
    for game_state in game_states:
        if game_state.status == Status.PLAYING_USER_FOUND:
            await send_mentions_message(ctx, game_state, "playing_users")
        elif game_state.status == Status.PLAYED_WORD:
            await send_user_words_message(game_state)
        elif game_state.status == Status.PLAYING_ORDER:
            await send_mentions_message(ctx, game_state, "playing_order")
        else:
            reply = generate_message(game_state.status.name, game_state.data)
            await ctx.send(reply)


@bot.command(name="eliminated")
@guild_only()
async def eliminate(ctx):
    game_states = controllers.eliminate(ctx.channel.id, ctx.author.id)
    for game_state in game_states:
        if game_state.status == Status.PLAYING_ORDER:
            await send_mentions_message(ctx, game_state, "playing_order")
        elif game_state.status == Status.ASK_GUESSED_WORD:
            user = bot.get_user(ctx.author.id)
            reply = generate_message(game_state.status.name, game_state.data)
            await user.send(reply)
        else:
            reply = generate_message(game_state.status.name, game_state.data)
            await ctx.send(reply)


async def greet(user):
    response = "Hi {mention}!".format(mention=user.mention)
    await user.send(response)


async def send_user_words_message(game_state):
    user_words = game_state.data
    for user_id in user_words:
        message = generate_message(game_state.status.name, user_words[user_id])
        user = bot.get_user(user_id)
        await user.send(message)


async def send_mentions_message(ctx, game_state, user_ids_key):
    user_ids = game_state.data[user_ids_key]
    data = {user_ids_key: generate_mentions(user_ids)}
    reply = generate_message(game_state.status.name, data)
    await ctx.send(reply)
