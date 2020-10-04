import asyncio
from datetime import datetime, timedelta
from functools import wraps

from discord import Colour, Embed
from discord.ext.commands import Cog, command, errors, guild_only

from discordbot.errors import EmptyUserArgumentFound, MultipleVotesFound
from discordbot.handlers import retrieve_player_ids, send_mention_message
from discordbot.helpers import CommandStatus, generate_message
from undercover import Status, controllers

POLLING_DURATION_IN_SECONDS = 30
EMBED_COLOR = Colour.blue()


def poll_started(func):
    @wraps(func)
    def wrapper(poll, *args, **kwargs):
        if poll.started:
            return func(poll, *args, **kwargs)

    return wrapper


class PollService:
    def __init__(self, cog, ctx):
        self.ctx = ctx
        self.bot = cog.bot
        self.embed_color = EMBED_COLOR
        self.duration = POLLING_DURATION_IN_SECONDS
        self.game_state = None
        self.instruction_msg = None
        self.status_msg = None
        self.timer_msg = None
        self.started = False
        self.alive_player_ids = list()

    async def start(self):
        await self.initiate_poll_messages()
        self.game_state = self.get_game_state()
        handle_start = self.get_handler()
        await handle_start()

    @poll_started
    async def complete(self):
        self.game_state = self.get_completed_state()
        handle_completed = self.get_handler()
        await handle_completed()

    def get_game_state(self):
        game_states = controllers.start_poll(
            self.ctx.channel.id, self.ctx.author.id, self.status_msg.id
        )
        for game_state in game_states:
            return game_state

    def get_completed_state(self):
        game_states = controllers.complete_poll(
            self.ctx.channel.id, self.alive_player_ids
        )
        for game_state in game_states:
            return game_state

    def get_handler(self):
        handlers = {
            Status.ONGOING_GAME_NOT_FOUND.name: self.handle_reply_to_channel,
            Status.ONGOING_POLL_FOUND.name: self.handle_reply_to_channel,
            Status.PLAYER_NOT_FOUND.name: self.handle_mention_players,
            Status.PLAYER_ALREADY_KILLED.name: self.handle_mention_players,
            Status.POLL_STARTED.name: self.handle_start_poll,
            Status.NO_VOTES_SUBMITTED.name: self.handle_failed_poll,
            Status.NOT_ENOUGH_VOTES.name: self.handle_failed_poll,
            Status.MULTIPLE_PLAYERS_VOTED.name: self.handle_failed_poll,
            Status.POLL_DECIDED.name: self.handle_poll_decided,
        }
        return handlers.get(self.game_state.status.name, self.default_handler)

    def default_handler(self):
        raise KeyError("No handler found")

    async def handle_mention_players(self, user_id_key="player"):
        await send_mention_message(self.ctx, self.game_state, user_id_key)
        await self.delete_poll_messages()

    async def handle_reply_to_channel(self):
        reply = generate_message(
            self.game_state.status.name, self.game_state.data
        )
        await self.ctx.send(reply)
        await self.delete_poll_messages()

    async def handle_start_poll(self):
        self.started = True
        self.alive_player_ids = self.game_state.data["players"]
        polling_tasks = self.generate_polling_tasks()
        embed = self.generate_instruction_embed()
        await self.instruction_msg.edit(content="", embed=embed)
        await self.status_msg.edit(content="No votes submitted yet")
        await asyncio.wait(polling_tasks, return_when=asyncio.FIRST_COMPLETED)

    async def handle_poll_decided(self):
        result_embed = self.generate_result_embed()
        await self.ctx.send(embed=result_embed)
        await self.handle_mention_players()

    async def handle_failed_poll(self):
        result_embed = self.generate_result_embed()
        await self.handle_reply_to_channel()
        await self.ctx.send(embed=result_embed)

    async def poll_timer(self):
        second = self.duration
        while second > 0:
            await self.timer_msg.edit(
                content=f"Time remaining **{second}** seconds"
            )
            await asyncio.sleep(1)
            second -= 1

    async def initiate_poll_messages(self):
        self.instruction_msg = await self.ctx.send("Generating new poll...")
        self.timer_msg = await self.ctx.send("\u200b")
        self.status_msg = await self.ctx.send("\u200b")

    async def delete_poll_messages(self):
        await self.instruction_msg.delete()
        await self.timer_msg.delete()
        await self.status_msg.delete()

    def generate_polling_tasks(self):
        reaction_listener = self.generate_reaction_listener()
        return [
            self.bot.wait_for("reaction_add", check=reaction_listener),
            self.poll_timer(),
        ]

    def generate_reaction_listener(self):
        def listener(reaction, user):
            return (
                user.id == self.status_msg.author.id
                and reaction.message.id == self.status_msg.id
            )

        return listener

    def generate_result_embed(self):
        if self.game_state.status == Status.NO_VOTES_SUBMITTED:
            description = "No votes submitted"
        else:
            tally = self.game_state.data["tally"]
            total_alive_players = len(self.alive_player_ids)
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
            colour=self.embed_color,
            timestamp=datetime.utcnow(),
        )

    def generate_instruction_embed(self):
        user_ids = self.alive_player_ids
        prefix = self.bot.command_prefix
        commands = "\n".join(
            [f"• `{prefix}vote` <@{user_id}>" for user_id in user_ids]
        )
        instruction = f"In the next **{self.duration} seconds**,\n\
                        Vote **one player** by running one of these commands below!\n\n\
                        **YOU CAN ONLY VOTE ONCE**\n\
                        \n\
                        {commands}"
        return Embed(
            title="[POLL] Instruction",
            description=instruction,
            colour=self.embed_color,
            timestamp=datetime.utcnow(),
        )


class Poll(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("Poll cog ready")

    @command(name="poll")
    @guild_only()
    async def handle_poll(self, ctx):
        poll = PollService(self, ctx)
        await poll.start()
        await poll.complete()


def setup(bot):
    bot.add_cog(Poll(bot))
