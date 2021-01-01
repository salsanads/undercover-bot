import asyncio
from datetime import datetime
from functools import wraps

from discord import Colour, Embed
from discord.ext.commands import Cog, command, guild_only

from discordbot import bot
from discordbot.helpers import send_message
from undercover import Status, controllers

from .helpers import register_cog


@register_cog
class Poll(Cog):
    @Cog.listener()
    async def on_ready(self):
        print("Poll cog ready")

    @command(name="poll")
    @guild_only()
    async def handle_poll(self, ctx):
        poll_worker = PollWorker(ctx)
        await poll_worker.start_poll()
        await poll_worker.complete_poll()


def poll_started(func):
    @wraps(func)
    def wrapper(poll_worker, *args, **kwargs):
        if poll_worker.started_poll:
            return func(poll_worker, *args, **kwargs)
        return asyncio.sleep(0)  # hack to return awaitable

    return wrapper


class PollWorker:
    POLL_DURATION = 30  # seconds

    def __init__(self, ctx):
        self.ctx = ctx
        self.poll_message = None
        self.started_poll = False

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
        await self.initiate_poll_message()
        game_states = controllers.start_poll(
            self.ctx.channel.id,
            self.ctx.author.id,
            self.poll_message.status.id,
        )
        handler = self.get_handler(game_states[0])
        await handler(self, game_states[0])

    @poll_started
    async def complete_poll(self):
        game_states = controllers.complete_poll(self.ctx.channel.id)
        handler = self.get_handler(game_states[0])
        await handler(self, game_states[0])

    async def initiate_poll_message(self):
        instruction = await self.ctx.send("Generating new poll...")
        timer = await self.ctx.send("\u200b")
        status = await self.ctx.send("\u200b")
        self.poll_message = PollMessage(instruction, timer, status)

    async def handle_invalid_poll(self, game_state, user_id_key="player"):
        if game_state.data is not None and user_id_key in game_state.data:
            await send_message(self.ctx, game_state, user_id_key)
        else:
            await send_message(self.ctx, game_state)
        await self.poll_message.delete()

    async def handle_started_poll(self, game_state):
        self.started_poll = True
        embed = self.generate_instruction_embed(game_state.data["players"])
        await self.poll_message.instruction.edit(content="", embed=embed)
        await self.poll_message.status.edit(content="No votes submitted yet")
        await asyncio.wait(
            [self.poll_timer()], return_when=asyncio.FIRST_COMPLETED
        )

    async def handle_decided_poll(self, game_state):
        result_embed = self.generate_result_embed(game_state, Colour.green())
        await self.ctx.send(embed=result_embed)
        await send_message(self.ctx, game_state, "player")
        await self.poll_message.delete()

    async def handle_failed_poll(self, game_state):
        result_embed = self.generate_result_embed(game_state, Colour.red())
        await self.ctx.send(embed=result_embed)
        await send_message(self.ctx, game_state)
        await self.poll_message.delete()

    async def poll_timer(self):
        second = self.POLL_DURATION
        while second > 0:
            await self.poll_message.timer.edit(
                content=f"Time remaining **{second}** seconds"
            )
            await asyncio.sleep(1)
            second -= 1

    @staticmethod
    def generate_instruction_embed(user_ids):
        commands = "\n".join(
            [
                f"• `{bot.command_prefix}vote` <@{user_id}>"
                for user_id in user_ids
            ]
        )
        instruction = f"In the next **{PollWorker.POLL_DURATION} seconds**,\n\
                        Vote **one player** by running one of these commands below!\n\n\
                        **YOU CAN ONLY VOTE ONCE**\n\
                        \n\
                        {commands}"
        return Embed(
            title="[POLL] Instruction",
            description=instruction,
            colour=Colour.blue(),
            timestamp=datetime.utcnow(),
        )

    @staticmethod
    def generate_result_embed(game_state, embed_color):
        if game_state.status == Status.NO_VOTES_SUBMITTED:
            description = "No votes submitted"
        else:
            tally = game_state.data["tally"]
            total_alive_players = len(game_state.data["players"])
            description = "\n".join(
                [
                    f"<@{user}> is voted by **{votes}** people"
                    for user, votes in tally.items()
                ]
            )
            description += (
                f"\n\nTotal alive players: **{total_alive_players}**"
            )
        return Embed(
            title="[POLL] Results",
            description=description,
            colour=embed_color,
            timestamp=datetime.utcnow(),
        )


class PollMessage:
    def __init__(self, instruction, timer, status):
        self.instruction = instruction
        self.timer = timer
        self.status = status

    async def delete(self):
        await self.instruction.delete()
        await self.timer.delete()
        await self.status.delete()
