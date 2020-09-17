from discord.ext import commands
from discord.ext.commands import Bot, dm_only, guild_only

from undercover import Status, controllers
from undercover.controllers.helpers import clear_game

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


@bot.command(name="howto")
async def handle_how_to(ctx):
    await send_how_to_message(ctx)


@bot.command(name="start")
@guild_only()
async def handle_start(ctx):
    channel_id = ctx.channel.id
    user_ids = retrieve_player_ids(ctx)
    game_states = controllers.start(str(channel_id), user_ids)
    for game_state in game_states:
        if game_state.status == Status.PLAYING_USER_FOUND:
            await send_mention_message(ctx, game_state, ["playing_users"])
        elif game_state.status == Status.PLAYED_WORD:
            await send_user_words_message(game_state)
        elif game_state.status == Status.PLAYING_ORDER:
            await send_how_to_message(ctx)
            await send_mention_message(ctx, game_state, ["playing_order"])
        else:
            reply = generate_message(game_state.status.name, game_state.data)
            await ctx.send(reply)


@bot.command(name="eliminated")
@guild_only()
async def handle_eliminate(ctx):
    game_states = controllers.eliminate(
        str(ctx.channel.id), str(ctx.author.id)
    )
    user = bot.get_user(ctx.author.id)
    for game_state in game_states:
        if game_state.status == Status.PLAYING_ORDER:
            await send_mention_message(ctx, game_state, ["playing_order"])
        elif (
            game_state.status == Status.ELIMINATED_PLAYER_NOT_FOUND
            or game_state.status == Status.ELIMINATED_PLAYER_ALREADY_KILLED
            or game_state.status == Status.CIVILIAN_ELIMINATED
            or game_state.status == Status.UNDERCOVER_ELIMINATED
            or game_state.status == Status.MR_WHITE_ELIMINATED
        ):
            await send_mention_message(ctx, game_state, ["player"])
        elif game_state.status == Status.ASK_GUESSED_WORD:
            reply = generate_message(game_state.status.name, game_state.data)
            await user.send(reply)
        elif game_state.status == Status.SUMMARY:
            await send_mention_message(
                ctx, game_state, ["civilians", "undercovers", "mr_whites"]
            )
        else:
            reply = generate_message(game_state.status.name, game_state.data)
            await ctx.send(reply)


@bot.command(name="guess")
@dm_only()
async def handle_guess(ctx):
    user_id = ctx.message.author.id
    word = " ".join(ctx.message.content.split(" ")[1:])
    game_states = controllers.guess(str(user_id), word)
    for game_state in game_states:
        if game_state.status == Status.PLAYING_ORDER:
            channel = bot.get_channel(int(game_state.room_id))
            await send_mention_message(channel, game_state, ["playing_order"])
        elif game_state.status == Status.NOT_IN_GUESSING_TURN:
            reply = generate_message(game_state.status.name, game_state.data)
            await ctx.send(reply)
        elif game_state.status == Status.SUMMARY:
            await send_mention_message(
                ctx, game_state, ["civilians", "undercovers", "mr_whites"]
            )
        else:
            channel = bot.get_channel(int(game_state.room_id))
            reply = generate_message(game_state.status.name, game_state.data)
            await channel.send(reply)


@bot.command(name="clear")
@guild_only()
async def handle_clear(ctx):
    clear_game(ctx.channel.id)
    await ctx.send("The game has been cleared")


async def send_how_to_message(ctx):
    reply = generate_message(CommandStatus.HOW_TO.name)
    await ctx.send(reply)


def retrieve_player_ids(ctx):
    user_ids = {str(ctx.author.id)}
    for user in ctx.message.mentions:
        if user.bot:
            raise BotPlayerFound
        user_ids.add(str(user.id))
    return list(user_ids)


async def send_user_words_message(game_state):
    user_words = game_state.data
    for user_id in user_words:
        message = generate_message(game_state.status.name, user_words[user_id])
        user = bot.get_user(int(user_id))
        await user.send(message)


async def send_mention_message(recipient, game_state, user_id_keys):
    for user_id_key in user_id_keys:
        if type(game_state.data[user_id_key]) == list:
            game_state.data[user_id_key] = generate_mention(
                user_ids=game_state.data[user_id_key]
            )
        else:
            game_state.data[user_id_key] = generate_mention(
                user_id=game_state.data[user_id_key]
            )

    message = generate_message(game_state.status.name, game_state.data)
    await recipient.send(message)
