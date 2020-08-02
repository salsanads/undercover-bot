import pytest

from undercover.controllers.helpers import get_elimination_result
from undercover.models import Player, PlayingRole
from undercover.payloads import GameState, Role, Status


class TestGetEliminationResult:
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
        "user_id1, user_id2, expected_result_status, expected_result_data, expected_returned_player, expected_returned_role",
        [
            (
                None,
                "1",
                Status.NON_CIVILIAN_WIN,
                None,
                "1",
                Role.CIVILIAN.name,
            ),
            (None, "3", Status.PLAYING_ORDER, list, "3", Role.UNDERCOVER.name),
            (
                None,
                "4",
                Status.ASK_GUESSED_WORD,
                None,
                "4",
                Role.MR_WHITE.name,
            ),
            ("4", "3", Status.CIVILIAN_WIN, None, "3", Role.UNDERCOVER.name),
        ],
    )
    def test_get_elimination_result(
        user_id1,
        user_id2,
        expected_result_status,
        expected_result_data,
        expected_returned_player,
        expected_returned_role,
        session,
    ):
        room_id = "1"
        if user_id1 is not None:
            Player.kill(user_id1)
        Player.kill(user_id2)

        last_killed_player = Player.get(user_id2)
        game_states = get_elimination_result(
            last_killed_player, return_eliminated_role=True
        )
        game_states_without_returned_role = get_elimination_result(
            last_killed_player
        )
        assert len(game_states) == 2
        assert len(game_states_without_returned_role) == 1

        returned_elimination_role = game_states[0]
        elimination_result = game_states[1]

        assert elimination_result.status is expected_result_status
        if elimination_result.status is not Status.PLAYING_ORDER:
            assert elimination_result.data is expected_result_data
        else:
            new_playing_order = elimination_result.data["playing_order"]
            assert isinstance(new_playing_order, expected_result_data)
            assert len(new_playing_order) == Player.num_alive_players(room_id)
            # manual check for randomness
            print(f"the new playing order is: {new_playing_order}")

        assert returned_elimination_role.status is Status.ELIMINATED_ROLE
        assert (
            returned_elimination_role.data["player"]
            == expected_returned_player
        )
        assert returned_elimination_role.data["role"] == expected_returned_role

        remaining_role = (
            session.query(PlayingRole).filter_by(room_id=room_id).first()
        )
        remaining_player = (
            session.query(Player).filter_by(room_id=room_id).first()
        )
        if elimination_result.status in (
            Status.CIVILIAN_WIN,
            Status.NON_CIVILIAN_WIN,
        ):
            assert remaining_role is None
            assert remaining_player is None
        else:
            assert remaining_role is not None
            assert remaining_player is not None
