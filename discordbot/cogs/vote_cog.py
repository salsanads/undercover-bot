from datetime import datetime

from discord import Colour, Embed
from discord.ext.commands import Cog, command, errors, guild_only

from discordbot.errors import EmptyVoteFound, MultipleVotesFound
from discordbot.helpers import (
    CommandStatus,
    generate_message,
    retrieve_player_ids,
    send_mention_message,
)
from undercover import Status, controllers

from .helpers import register_cog

EMBED_COLOR = Colour.blue()


class VoteHandler:
    def __init__(self, ctx):
        self.ctx = ctx
        self.game_state = self.get_game_state()
        self.handler = self.get_handler()
        self.embed_color = EMBED_COLOR

    async def respond(self):
        await self.handler()

    def get_game_state(self):
        voted_id = self.get_voted_id()
        game_states = controllers.vote_player(
            self.ctx.channel.id, voted_id, self.ctx.author.id
        )
        for game_state in game_states:
            return game_state

    def get_voted_id(self):
        voted_ids = retrieve_player_ids(self.ctx, include_author=False)
        if self.valid_voted_id(voted_ids):
            return voted_ids[0]

    def valid_voted_id(self, voted_ids):
        if len(voted_ids) > 1:
            raise MultipleVotesFound
        elif len(voted_ids) == 0:
            raise EmptyVoteFound
        return True

    def get_handler(self):
        handlers = {
            Status.ONGOING_POLL_NOT_FOUND.name: self.handle_reply_to_channel,
            Status.PLAYER_NOT_FOUND.name: self.handle_mention_players,
            Status.PLAYER_ALREADY_KILLED.name: self.handle_mention_players,
            Status.VOTE_EXISTS.name: self.handle_mention_players,
            Status.VOTE_SUCCESS.name: self.handle_update_status_message,
            Status.TOTAL_VOTES_REACHED.name: self.handle_add_completed_reaction,
        }
        return handlers.get(self.game_state.status.name, self.default_handler)

    def default_handler(self):
        raise KeyError("No handler found")

    async def handle_mention_players(self, user_id_key="player"):
        await send_mention_message(self.ctx, self.game_state, user_id_key)

    async def handle_reply_to_channel(self):
        reply = generate_message(
            self.game_state.status.name, self.game_state.data
        )
        await self.ctx.send(reply)

    async def handle_add_completed_reaction(self):
        msg_id = self.game_state.data["msg_id"]
        poll_msg = await self.ctx.fetch_message(msg_id)
        await poll_msg.add_reaction("👍")

    async def handle_update_status_message(self):
        msg_id = self.game_state.data["msg_id"]
        status_embed = self.generate_status_embed()
        poll_msg = await self.ctx.fetch_message(msg_id)
        await poll_msg.edit(content="", embed=status_embed)

    def generate_status_embed(self):
        tally = self.game_state.data["tally"]
        return Embed(
            title="[POLL] Status",
            description="\n".join(
                [
                    f"<@{user}> is voted by **{votes}** people"
                    for user, votes in tally.items()
                ]
            ),
            colour=self.embed_color,
            timestamp=datetime.utcnow(),
        )


@register_cog
class Vote(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("Vote cog ready")

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, errors.CommandInvokeError):
            if isinstance(error.original, MultipleVotesFound):
                await ctx.send(
                    generate_message(CommandStatus.MULTIPLE_VOTES_FOUND.name)
                )
            if isinstance(error.original, EmptyVoteFound):
                await ctx.send(
                    generate_message(CommandStatus.EMPTY_VOTE_FOUND.name)
                )

    @command(name="vote")
    @guild_only()
    async def handle_vote(self, ctx):
        vote_handler = VoteHandler(ctx)
        await vote_handler.respond()
