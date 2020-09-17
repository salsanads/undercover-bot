import pytest

from undercover.controllers.eliminate_controller import eliminate, kill_player
from undercover.models import Player, PlayingRole
from undercover.payloads import GameState, Role, Status


class TestEliminateController:
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
        "user_id, expected_guessing", [("1", False), ("4", True)],
    )
    def test_kill_player(user_id, expected_guessing):
        kill_player(user_id)
        killed_player = Player.get(user_id)
        assert not killed_player.alive
        assert killed_player.guessing is expected_guessing

    @staticmethod
    def test_kill_player_with_non_existing_player():
        non_existing_user_id = "5"
        with pytest.raises(Exception):
            kill_player(non_existing_user_id)

    @staticmethod
    @pytest.mark.parametrize(
        "already_killed_user_ids, eliminated_user_id, eliminated_role, expected_status",
        [
            ([], "1", Role.CIVILIAN.name, Status.NON_CIVILIAN_WIN),
            ([], "3", Role.UNDERCOVER.name, Status.PLAYING_ORDER),
            ([], "4", Role.MR_WHITE.name, Status.ASK_GUESSED_WORD),
            (["4"], "3", Role.UNDERCOVER.name, Status.CIVILIAN_WIN),
        ],
    )
    def test_eliminate_valid_scenario(
        already_killed_user_ids,
        eliminated_user_id,
        eliminated_role,
        expected_status,
    ):
        room_id = "1"
        for user_id in already_killed_user_ids:
            kill_player(user_id)

        game_states = eliminate(room_id, eliminated_user_id)
        assert len(game_states) == 2

        role_game_state = game_states[0]
        if eliminated_role == Role.CIVILIAN.name:
            assert role_game_state.status is Status.CIVILIAN_ELIMINATED
        elif eliminated_role == Role.UNDERCOVER.name:
            assert role_game_state.status is Status.UNDERCOVER_ELIMINATED
        else:
            assert role_game_state.status is Status.MR_WHITE_ELIMINATED
        assert "player" in role_game_state.data
        assert role_game_state.data["player"] == eliminated_user_id
        assert "role" in role_game_state.data
        assert role_game_state.data["role"] == eliminated_role

        result_game_state = game_states[1]
        assert result_game_state.status is expected_status

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
        kill_player("2")

        game_states = eliminate(room_id, user_id)
        assert len(game_states) == 1

        game_state = game_states[0]
        assert game_state.status is expected_status

        PlayingRole.delete("2")
        Player.delete("2")
