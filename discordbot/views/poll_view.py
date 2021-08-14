import math
from typing import Callable, Coroutine

from discord import ButtonStyle, Colour, Embed, Interaction, TextChannel
from discord.ui import Button, View

from discordbot.helpers import (
    MessageKey,
    generate_mention,
    generate_message,
    send_message,
)
from undercover import Status, controllers


class PollItem:
    def __init__(self, item_id: str, label: str):
        self.item_id = item_id
        self.label = label


class PollView(View):
    MAX_NUM_COLUMNS = 5

    def __init__(self, poll_items: [PollItem]):
        super().__init__()
        num_rows = math.ceil(len(poll_items) / PollView.MAX_NUM_COLUMNS)
        for col in range(min(len(poll_items), PollView.MAX_NUM_COLUMNS)):
            for row in range(num_rows):
                i = row * PollView.MAX_NUM_COLUMNS + col
                self.add_item(
                    PollButton(poll_items[i], row, VoteHandler.handle_vote)
                )


class PollButton(Button):
    def __init__(
        self,
        poll_item: PollItem,
        row: int,
        inner_callback: Callable[[TextChannel, str, str], Coroutine],
    ):
        super().__init__(
            style=ButtonStyle.secondary, label=poll_item.label, row=row
        )
        self.poll_item = poll_item
        self.inner_callback = inner_callback

    async def callback(self, interaction: Interaction):
        await self.inner_callback(
            interaction.channel, self.poll_item.item_id, interaction.user.id
        )


class VoteHandler:
    @staticmethod
    async def handle_vote(
        channel: TextChannel, voted_user_id: str, voter_user_id: str
    ):
        game_states = controllers.vote_player(
            channel.id, voted_user_id, voter_user_id
        )
        handler = VoteHandler.get_handler(game_states[0])
        await handler(channel, game_states[0])

    @staticmethod
    def get_handler(game_state):
        handlers = {
            Status.ONGOING_POLL_NOT_FOUND.name: VoteHandler.handle_invalid_vote,
            Status.PLAYER_NOT_FOUND.name: VoteHandler.handle_invalid_vote,
            Status.PLAYER_ALREADY_KILLED.name: VoteHandler.handle_invalid_vote,
            Status.VOTE_EXISTS.name: VoteHandler.handle_invalid_vote,
            Status.VOTE_SUCCESS.name: VoteHandler.handle_success_vote,
            Status.TOTAL_VOTES_REACHED.name: VoteHandler.handle_success_vote,
        }
        return handlers.get(game_state.status.name)

    @staticmethod
    async def handle_invalid_vote(channel, game_state, user_id_key="player"):
        if game_state.data is not None and user_id_key in game_state.data:
            await send_message(channel, game_state, user_id_key)
        else:
            await send_message(channel, game_state)

    @staticmethod
    async def handle_success_vote(ctx, game_state):
        poll_msg = await ctx.fetch_message(game_state.data["msg_id"])
        embed = VoteHandler.generate_status_embed(game_state)
        await poll_msg.edit(embed=embed)

    @staticmethod
    def generate_status_embed(game_state):
        tally = game_state.data["tally"]
        voters = game_state.data["voters"]
        voted_player_info = generate_message(
            MessageKey.POLL_STATUS_VOTED_PLAYER_INFO
        )
        return Embed(
            title=generate_message(MessageKey.POLL_STATUS_TITLE),
            description="\n".join(
                [
                    voted_player_info.format(
                        user_id=user_id,
                        vote_count=vote_count,
                        voters=generate_mention(user_ids=voters[user_id]),
                    )
                    for user_id, vote_count in tally.items()
                ]
            ),
            colour=Colour.blue(),
        )
