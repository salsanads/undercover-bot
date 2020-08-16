import pytest

from undercover.controllers.eliminate_controller import kill_player
from undercover.controllers.helpers import evaluate_game
from undercover.models import Player, PlayingRole
from undercover.payloads import GameState, Role, Status


class TestEvaluateGame:
    @staticmethod
    @pytest.fixture(autouse=True)
    def populate_db():
        PlayingRole.insert(
            PlayingRole("1", Role.CIVILIAN.name, "civilian_word")
        )
        PlayingRole.insert(
            PlayingRole("1", Role.UNDERCOVER.name, "undercover_word")
        )
        PlayingRole.insert(PlayingRole("1", Role.MR_WHITE.name))
        Player.insert(Player("1", "1", Role.CIVILIAN.name))
        Player.insert(Player("2", "1", Role.CIVILIAN.name))
        Player.insert(Player("3", "1", Role.UNDERCOVER.name))
        Player.insert(Player("4", "1", Role.MR_WHITE.name))
        yield
        PlayingRole.delete("1")
        Player.delete("1")

    @staticmethod
    @pytest.mark.parametrize(
        "killed_user_ids, expected_status",
        [
            (["1"], Status.NON_CIVILIAN_WIN),
            (["3"], Status.PLAYING_ORDER),
            (["4", "3"], Status.CIVILIAN_WIN),
        ],
    )
    def test_evaluate_game(killed_user_ids, expected_status, session):
        room_id = "1"
        for user_id in killed_user_ids:
            kill_player(user_id)

        game_state = evaluate_game(room_id)

        assert game_state.status is expected_status
        if game_state.status is not Status.PLAYING_ORDER:
            assert game_state.data is None
        else:
            new_playing_order = game_state.data["playing_order"]
            assert isinstance(new_playing_order, list)
            assert len(new_playing_order) == Player.num_alive_players(room_id)
            print(f"the new playing order is: {new_playing_order}")

        remaining_role = (
            session.query(PlayingRole).filter_by(room_id=room_id).first()
        )
        remaining_player = (
            session.query(Player).filter_by(room_id=room_id).first()
        )
        if game_state.status is not Status.PLAYING_ORDER:
            assert remaining_role is None
            assert remaining_player is None
        else:
            assert remaining_role is not None
            assert remaining_player is not None
