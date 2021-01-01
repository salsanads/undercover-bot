import asyncio
import traceback

from discord import Activity, ActivityType
from discord.ext import commands
from discord.ext.commands import dm_only, guild_only

from discordbot import bot
from undercover import Status, controllers, models
from undercover.controllers.helpers import clear_game

from .errors import BotPlayerFound
from .helpers import (
    MessageStatus,
    generate_mention,
    generate_message,
    retrieve_player_ids,
    send_message,
)

SHOW_PLAYED_WORDS_DURATION = 5  # seconds


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")
    await bot.change_presence(
        activity=Activity(type=ActivityType.listening, name="!help")
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.send(generate_message(MessageStatus.GUILD_ONLY_COMMAND))
    elif isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.send(generate_message(MessageStatus.DM_ONLY_COMMAND))
    elif isinstance(error, commands.errors.CommandInvokeError):
        if isinstance(error.original, BotPlayerFound):
            await ctx.send(generate_message(MessageStatus.BOT_PLAYER_FOUND))
        else:
            traceback.print_exception(type(error), error, error.__traceback__)
    else:
        traceback.print_exception(type(error), error, error.__traceback__)


@bot.command(name="howto")
async def handle_how_to(ctx):
    """Shows game guide"""
    await send_how_to_message(ctx)


@bot.command(name="start")
@guild_only()
async def handle_start(ctx):
    """Starts the game"""
    user_ids = retrieve_player_ids(ctx)
    game_states = controllers.start_game(ctx.channel.id, user_ids)
    for game_state in game_states:
        if game_state.status == Status.PLAYING_USER_FOUND:
            await send_message(ctx, game_state, "playing_users")
        elif game_state.status == Status.PLAYED_WORD:
            await send_user_word_messages(game_state, ctx.channel.id)
        elif game_state.status == Status.PLAYING_ORDER:
            await send_how_to_message(ctx)
            await send_message(ctx, game_state, "playing_order")
        else:
            await send_message(ctx, game_state)


@bot.command(name="eliminated")
@guild_only()
async def handle_eliminate(ctx):
    """Eliminates own self"""
    game_states = controllers.eliminate_player(ctx.channel.id, ctx.author.id)
    user = bot.get_user(ctx.author.id)
    for game_state in game_states:
        if game_state.status == Status.PLAYING_ORDER:
            await send_message(ctx, game_state, "playing_order")
        elif (
            game_state.status == Status.PLAYER_NOT_FOUND
            or game_state.status == Status.PLAYER_ALREADY_KILLED
            or game_state.status == Status.CIVILIAN_ELIMINATED
            or game_state.status == Status.UNDERCOVER_ELIMINATED
            or game_state.status == Status.MR_WHITE_ELIMINATED
        ):
            await send_message(ctx, game_state, "player")
        elif game_state.status == Status.ASK_GUESSED_WORD:
            reply = generate_message(game_state.status, game_state.data)
            await user.send(reply)
        elif game_state.status == Status.SUMMARY:
            await send_summary_message(ctx, game_state)
            await delete_user_word_messages(ctx.channel.id)
        else:
            await send_message(ctx, game_state)


@bot.command(name="guess")
@dm_only()
async def handle_guess(ctx):
    """Guesses Civilian's word"""
    user_id = ctx.message.author.id
    word = " ".join(ctx.message.content.split(" ")[1:])
    game_states = controllers.guess_word(user_id, word)
    for game_state in game_states:
        if game_state.status == Status.PLAYING_ORDER:
            channel = bot.get_channel(game_state.room_id)
            await send_message(channel, game_state, "playing_order")
        elif game_state.status == Status.NOT_IN_GUESSING_TURN:
            await send_message(ctx, game_state)
        elif game_state.status == Status.SUMMARY:
            await send_summary_message(ctx, game_state)
            await delete_user_word_messages(ctx.channel.id)
        else:
            channel = bot.get_channel(game_state.room_id)
            reply = generate_message(game_state.status, game_state.data)
            await channel.send(reply)


@bot.command(name="clear")
@guild_only()
async def handle_clear(ctx):
    """Clears the game"""
    clear_game(ctx.channel.id)
    await ctx.send("The game has been cleared")
    await delete_user_word_messages(ctx.channel.id)


async def send_how_to_message(ctx):
    reply = generate_message(MessageStatus.HOW_TO_COMMAND)
    await ctx.send(reply)


async def send_user_word_messages(game_state, channel_id):
    user_words = game_state.data
    word_messages = []
    for user_id in user_words:
        user = bot.get_user(user_id)
        content = generate_message(game_state.status, user_words[user_id])
        message = await user.send(content)
        word_messages.append(
            models.WordMessage(message.id, user.id, channel_id)
        )
    models.WordMessage.insert_all(word_messages)


async def send_summary_message(ctx, game_state):
    players_keys = ["civilians", "undercovers", "mr_whites"]
    for players_key in players_keys:
        players = game_state.data[players_key]
        mentions = []
        for player in players:
            if player["alive"]:
                mentions.append(generate_mention(user_id=player["user_id"]))
            else:
                mentions.append(
                    generate_mention(
                        user_id=player["user_id"], style="~~{mention}~~"
                    )
                )
        one_line_mentions = " ".join(mentions)
        game_state.data[players_key] = one_line_mentions
    content = generate_message(game_state.status, game_state.data)
    message = await ctx.send(content)

    await asyncio.sleep(SHOW_PLAYED_WORDS_DURATION)

    game_state.data["civilian_word"] = "*deleted*"
    game_state.data["undercover_word"] = "*deleted*"
    content = generate_message(game_state.status, game_state.data)
    await message.edit(content=content)


async def delete_user_word_messages(channel_id):
    word_messages = models.WordMessage.get_all(channel_id)
    for word_message in word_messages:
        user = bot.get_user(word_message.user_id)
        message = await user.fetch_message(word_message.message_id)
        await message.delete()
    models.WordMessage.delete_all(channel_id)
