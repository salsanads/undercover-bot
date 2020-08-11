import pytest

from undercover.controllers.eliminate_controller import eliminate
from undercover.models import Player, PlayingRole
from undercover.payloads import GameState, Role, Status


class TestEliminate:
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
        "killed_user_ids, eliminated_user_id, eliminated_role, expected_status",
        [
            ([None], "1", Role.CIVILIAN.name, Status.NON_CIVILIAN_WIN),
            ([None], "3", Role.UNDERCOVER.name, Status.PLAYING_ORDER),
            ([None], "4", Role.MR_WHITE.name, Status.ASK_GUESSED_WORD),
            (["4"], "3", Role.UNDERCOVER.name, Status.CIVILIAN_WIN),
        ],
    )
    def test_eliminate_valid_scenario(
        killed_user_ids, eliminated_user_id, eliminated_role, expected_status
    ):
        room_id = "1"
        for user_id in killed_user_ids:
            if user_id is not None:
                Player.kill(user_id)

        game_states = eliminate(room_id, eliminated_user_id)
        assert len(game_states) == 2

        returned_elimination_role = game_states[0]
        assert returned_elimination_role.status is Status.ELIMINATED_ROLE
        assert "player" in returned_elimination_role.data
        assert returned_elimination_role.data["player"] == eliminated_user_id
        assert "role" in returned_elimination_role.data
        assert returned_elimination_role.data["role"] == eliminated_role

        elimination_result = game_states[1]
        assert elimination_result.status is expected_status

    @staticmethod
    @pytest.mark.parametrize(
        "room_id, user_id, expected_status",
        [
            ("3", "1", Status.ONGOING_GAME_NOT_FOUND),
            ("1", "7", Status.ELIMINATED_PLAYER_NOT_FOUND),
            ("2", "1", Status.ELIMINATED_PLAYER_NOT_FOUND),
            ("1", "2", Status.ELIMINATED_PLAYER_ALREADY_KILLED),
        ],
    )
    def test_eliminate_invalid_scenario(room_id, user_id, expected_status):
        PlayingRole.insert(PlayingRole("2", Role.MR_WHITE.name))
        Player.insert(Player("5", "2", Role.MR_WHITE.name))
        Player.kill("2")

        game_states = eliminate(room_id, user_id)
        assert len(game_states) == 1

        game_state = game_states[0]
        assert game_state.status is expected_status

        PlayingRole.delete("2")
        Player.delete("2")
