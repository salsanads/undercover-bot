import asyncio
from datetime import datetime
from functools import wraps

from discord import Colour, Embed
from discord.ext.commands import Cog, command, guild_only

from discordbot import bot
from discordbot.handlers import handle_eliminate
from discordbot.helpers import (
    MessageKey,
    command_desc,
    generate_message,
    generate_message_from_game_state,
    send_message,
)
from undercover import Status, controllers

from .helpers import register_cog


@register_cog
class Poll(Cog):
    @Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} cog ready")

    @command(name="poll", description=command_desc.get("POLL"))
    @guild_only()
    async def handle_poll(self, ctx):
        """Holds a poll to vote who will be eliminated in the current turn."""
        poll_worker = PollWorker(ctx)
        await poll_worker.start_poll()
        await poll_worker.complete_poll()


def poll_started(func):
    @wraps(func)
    def wrapper(poll_worker, *args, **kwargs):
        if poll_worker.poll_started:
            return func(poll_worker, *args, **kwargs)
        return asyncio.sleep(0)  # hack to return awaitable

    return wrapper


class PollWorker:
    POLL_DURATION = 30  # seconds

    def __init__(self, ctx):
        self.ctx = ctx
        self.poll_message = None
        self.poll_started = False

    @staticmethod
    def get_handler(game_state):
        handlers = {
            Status.ONGOING_GAME_NOT_FOUND.name: PollWorker.handle_invalid_poll,
            Status.ONGOING_POLL_FOUND.name: PollWorker.handle_invalid_poll,
            Status.PLAYER_NOT_FOUND.name: PollWorker.handle_invalid_poll,
            Status.PLAYER_ALREADY_KILLED.name: PollWorker.handle_invalid_poll,
            Status.POLL_STARTED.name: PollWorker.handle_started_poll,
            Status.NO_VOTES_SUBMITTED.name: PollWorker.handle_failed_poll,
            Status.NOT_ENOUGH_VOTES.name: PollWorker.handle_failed_poll,
            Status.MULTIPLE_PLAYERS_VOTED.name: PollWorker.handle_failed_poll,
            Status.POLL_DECIDED.name: PollWorker.handle_decided_poll,
        }
        return handlers.get(game_state.status.name)

    async def start_poll(self):
        self.poll_message = await self.ctx.send(
            generate_message(MessageKey.POLL_GENERATING_PROCESS)
        )
        game_states = controllers.start_poll(
            self.ctx.channel.id, self.ctx.author.id, self.poll_message.id,
        )
        handler = self.get_handler(game_states[0])
        await handler(self, game_states[0])

    @poll_started
    async def complete_poll(self):
        game_states = controllers.complete_poll(self.ctx.channel.id)
        handler = self.get_handler(game_states[0])
        await handler(self, game_states[0])

    async def handle_invalid_poll(self, game_state, user_id_key="player"):
        if game_state.data is not None and user_id_key in game_state.data:
            await self.poll.edit(
                content=generate_message_from_game_state(
                    game_state, user_id_key
                )
            )
        else:
            await self.poll_message.edit(
                content=generate_message_from_game_state(game_state)
            )

    async def handle_started_poll(self, game_state):
        self.poll_started = True
        await self.poll_message.edit(
            content=generate_message(MessageKey.POLL_STARTED)
        )
        await self.ctx.send(
            content="",
            embed=self.generate_instruction_embed(game_state.data["players"]),
        )
        await asyncio.wait([self.timer()], return_when=asyncio.FIRST_COMPLETED)

    async def handle_decided_poll(self, game_state):
        result_embed = self.generate_result_embed(game_state, Colour.green())
        await self.ctx.send(embed=result_embed)
        await send_message(self.ctx, game_state, "player")
        await handle_eliminate(self.ctx)

    async def handle_failed_poll(self, game_state):
        result_embed = self.generate_result_embed(game_state, Colour.red())
        await self.ctx.send(embed=result_embed)
        await self.poll_message.edit(
            content=generate_message_from_game_state(game_state)
        )

    async def timer(self):
        second = self.POLL_DURATION
        timer_message_content = generate_message(MessageKey.POLL_TIMER)
        timer_message = await self.ctx.send(
            timer_message_content.format(second=second)
        )
        while second > 0:
            # hack to check total votes reached while the timer on
            # TODO improve to not check every seconds (e.g. get notification when the last vote given)
            game_states = controllers.vote_controller.decide_vote_states(
                self.ctx.channel.id
            )
            if game_states[0].status == Status.TOTAL_VOTES_REACHED:
                await timer_message.edit(
                    content="{timer}\n{completed}".format(
                        timer=timer_message_content.format(second=second),
                        completed=generate_message(MessageKey.POLL_COMPLETED),
                    )
                )
                second = 0
            else:
                await asyncio.sleep(1)
                second -= 1
                await timer_message.edit(
                    content=timer_message_content.format(second=second)
                )

    @staticmethod
    def generate_instruction_embed(user_ids):
        commands = "\n".join(
            [
                f"• `{bot.command_prefix}vote` <@{user_id}>"
                for user_id in user_ids
            ]
        )
        instruction = generate_message(MessageKey.POLL_INSTRUCTION_CONTENT)
        return Embed(
            title=generate_message(MessageKey.POLL_INSTRUCTION_TITLE),
            description=instruction.format(
                poll_duration=PollWorker.POLL_DURATION, commands=commands
            ),
            colour=Colour.blue(),
            timestamp=datetime.utcnow(),
        )

    @staticmethod
    def generate_result_embed(game_state, embed_color):
        if game_state.status == Status.NO_VOTES_SUBMITTED:
            description = generate_message(
                MessageKey.POLL_RESULT_NO_VOTES_SUBMITTED
            )
        else:
            tally = game_state.data["tally"]
            voted_player_info = generate_message(
                MessageKey.POLL_RESULT_VOTED_PLAYER_INFO
            )
            total_alive_players = len(game_state.data["players"])
            description = "\n".join(
                [
                    voted_player_info.format(user=user, votes=votes)
                    for user, votes in tally.items()
                ]
            )
            result_info = generate_message(MessageKey.POLL_RESULT_INFO)
            description += "\n\n" + result_info.format(
                total_alive_players=total_alive_players
            )
        return Embed(
            title=generate_message(MessageKey.POLL_RESULT_TITLE),
            description=description,
            colour=embed_color,
            timestamp=datetime.utcnow(),
        )
