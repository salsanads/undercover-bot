from datetime import datetime

from discord import Colour, Embed
from discord.ext.commands import Cog, command, errors, guild_only

from discordbot.errors import EmptyVoteFound, MultipleVotesFound
from discordbot.helpers import (
    MessageKey,
    generate_message,
    retrieve_player_ids,
    send_message,
)
from undercover import Status, controllers

from .helpers import register_cog


@register_cog
class Vote(Cog):
    @Cog.listener()
    async def on_ready(self):
        print("Vote cog ready")

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, errors.CommandInvokeError):
            if isinstance(error.original, MultipleVotesFound):
                await ctx.send(
                    generate_message(MessageKey.MULTIPLE_VOTES_FOUND)
                )
            if isinstance(error.original, EmptyVoteFound):
                await ctx.send(generate_message(MessageKey.EMPTY_VOTE_FOUND))

    @command(name="vote")
    @guild_only()
    async def handle_vote(self, ctx):
        await VoteHandler.handle_vote(ctx)


class VoteHandler:
    @staticmethod
    async def handle_vote(ctx):
        game_state = VoteHandler.decide_game_state(ctx)
        handler = VoteHandler.get_handler(game_state)
        await handler(ctx, game_state)

    @staticmethod
    def get_handler(game_state):
        handlers = {
            Status.ONGOING_POLL_NOT_FOUND.name: VoteHandler.handle_invalid_vote,
            Status.PLAYER_NOT_FOUND.name: VoteHandler.handle_invalid_vote,
            Status.PLAYER_ALREADY_KILLED.name: VoteHandler.handle_invalid_vote,
            Status.VOTE_EXISTS.name: VoteHandler.handle_invalid_vote,
            Status.VOTE_SUCCESS.name: VoteHandler.handle_success_vote,
            Status.TOTAL_VOTES_REACHED.name: VoteHandler.handle_completed_vote,
        }
        return handlers.get(game_state.status.name)

    @staticmethod
    def decide_game_state(ctx):
        voted_user_id = VoteHandler.get_voted_user_id(ctx)
        game_states = controllers.vote_player(
            ctx.channel.id, voted_user_id, ctx.author.id
        )
        return game_states[0]

    @staticmethod
    def get_voted_user_id(ctx):
        voted_ids = retrieve_player_ids(ctx, include_author=False)
        if VoteHandler.voted_user_id_valid(voted_ids):
            return voted_ids[0]

    @staticmethod
    def voted_user_id_valid(voted_ids):
        if len(voted_ids) > 1:
            raise MultipleVotesFound
        elif len(voted_ids) == 0:
            raise EmptyVoteFound
        return True

    @staticmethod
    async def handle_invalid_vote(ctx, game_state, user_id_key="player"):
        if game_state.data is not None and user_id_key in game_state.data:
            await send_message(ctx, game_state, user_id_key)
        else:
            await send_message(ctx, game_state)

    @staticmethod
    async def handle_success_vote(ctx, game_state):
        msg_id = game_state.data["msg_id"]
        status_embed = VoteHandler.generate_status_embed(game_state)
        poll_msg = await ctx.fetch_message(msg_id)
        await poll_msg.edit(content="", embed=status_embed)

    @staticmethod
    async def handle_completed_vote(ctx, game_state):
        await VoteHandler.handle_success_vote(ctx, game_state)
        msg_id = game_state.data["msg_id"]
        poll_msg = await ctx.fetch_message(msg_id)
        await poll_msg.add_reaction("👍")

    @staticmethod
    def generate_status_embed(game_state):
        tally = game_state.data["tally"]
        voted_player_info = generate_message(
            MessageKey.POLL_STATUS_VOTED_PLAYER_INFO
        )
        return Embed(
            title=generate_message(MessageKey.POLL_STATUS_TITLE),
            description="\n".join(
                [
                    voted_player_info.format(user=user, votes=votes)
                    for user, votes in tally.items()
                ]
            ),
            colour=Colour.blue(),
            timestamp=datetime.utcnow(),
        )
