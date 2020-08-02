import pytest

from undercover.models.player import Player, PlayingRole
from undercover.payloads import Role


class TestPlayer:
    @staticmethod
    @pytest.fixture(autouse=True)
    def populate_db(session):
        session.add(PlayingRole("1", Role.CIVILIAN.name, "civilian_word"))
        session.add(PlayingRole("1", Role.UNDERCOVER.name, "undercover_word"))
        session.add(PlayingRole("1", Role.MR_WHITE.name))
        session.add(PlayingRole("2", Role.CIVILIAN.name, "civilian_word"))
        session.commit()
        yield
        session.query(PlayingRole).delete()
        session.query(Player).delete()

    @staticmethod
    def test_insert_player(session):
        playing_role = PlayingRole("1", Role.CIVILIAN.name, "civilian_word")
        civilian = Player(
            user_id="1",
            alive=True,
            guessing=False,
            room_id=playing_role.room_id,
            role=playing_role.role,
        )
        Player.insert(civilian)
        players = session.query(Player).filter_by(user_id="1").all()

        assert len(players) == 1
        player = players[0]
        assert player.user_id == "1"
        assert player.alive
        assert not player.guessing
        assert player.role == playing_role.role
        assert player.room_id == playing_role.room_id
        assert player.playing_role.word == playing_role.word

    @staticmethod
    def test_insert_duplicate_player(session):
        civilian = Player(
            user_id="1",
            alive=True,
            guessing=False,
            room_id="1",
            role=Role.CIVILIAN.name,
        )
        Player.insert(civilian)
        with pytest.raises(Exception):
            undercover = Player(
                user_id="1",
                alive=True,
                guessing=False,
                room_id="2",
                role=Role.UNDERCOVER.name,
            )
            Player.insert(undercover)

    @staticmethod
    def test_delete(session):
        user_ids = ["1", "2", "3"]
        room_ids = ["1", "1", "2"]
        for user_id, room_id in zip(user_ids, room_ids):
            player = Player(
                user_id=user_id, room_id=room_id, role=Role.CIVILIAN.name
            )
            Player.insert(player)

        to_be_deleted_room_id = "1"
        intact_room_id = "2"
        Player.delete(to_be_deleted_room_id)

        should_be_none = (
            session.query(Player)
            .filter_by(room_id=to_be_deleted_room_id)
            .first()
        )
        should_not_none = (
            session.query(Player).filter_by(room_id=intact_room_id).first()
        )
        assert should_be_none is None
        assert should_not_none is not None

    @staticmethod
    def test_num_alive_players(session):
        room_id = "1"
        user_ids = ["1", "2", "3", "4"]
        status = [True, True, False, True]
        roles = [
            Role.CIVILIAN.name,
            Role.CIVILIAN.name,
            Role.MR_WHITE.name,
            Role.UNDERCOVER.name,
        ]
        for user_id, alive, role in zip(user_ids, status, roles):
            player = Player(
                user_id=user_id, alive=alive, role=role, room_id=room_id
            )
            Player.insert(player)

        n_alive_players = Player.num_alive_players(room_id)
        n_alive_civilians = Player.num_alive_players(
            room_id, role=Role.CIVILIAN.name
        )
        n_alive_undercover = Player.num_alive_players(
            room_id, role=Role.UNDERCOVER.name
        )
        n_alive_mr_white = Player.num_alive_players(
            room_id, role=Role.MR_WHITE.name
        )

        assert n_alive_players == 3
        assert n_alive_civilians == 2
        assert n_alive_undercover == 1
        assert n_alive_mr_white == 0

    @staticmethod
    def test_alive_player_ids(session):
        room_id = "1"
        user_ids = ["1", "2", "3", "4"]
        status = [True, True, False, True]
        roles = [
            Role.CIVILIAN.name,
            Role.CIVILIAN.name,
            Role.MR_WHITE.name,
            Role.UNDERCOVER.name,
        ]
        for user_id, alive, role in zip(user_ids, status, roles):
            player = Player(
                user_id=user_id, alive=alive, role=role, room_id=room_id
            )
            Player.insert(player)

        alive_players_ids = Player.alive_player_ids(room_id)
        alive_civilians_ids = Player.alive_player_ids(
            room_id, role=Role.CIVILIAN.name
        )
        alive_undercover_ids = Player.alive_player_ids(
            room_id, role=Role.UNDERCOVER.name
        )
        alive_mr_white_ids = Player.alive_player_ids(
            room_id, role=Role.MR_WHITE.name
        )

        assert alive_players_ids == ["1", "2", "4"]
        assert alive_civilians_ids == ["1", "2"]
        assert alive_undercover_ids == ["4"]
        assert alive_mr_white_ids == []

    @staticmethod
    def test_get():
        user_id = "1"
        room_id = "1"
        Player.insert(Player(user_id, room_id, Role.CIVILIAN.name))
        player = Player.get(user_id)

        assert isinstance(player, Player)
        assert player.user_id == user_id
        assert player.room_id == room_id
        assert player.role == Role.CIVILIAN.name

    @staticmethod
    def test_get_non_existing_player():
        user_id = "1"
        assert Player.get(user_id) is None

    @staticmethod
    @pytest.mark.parametrize(
        "user_id, role, expected_guessing",
        [("1", Role.CIVILIAN.name, False), ("2", Role.MR_WHITE.name, True)],
    )
    def test_kill(user_id, role, expected_guessing):
        room_id = "1"
        player = Player(user_id, room_id, role)
        Player.insert(player)
        Player.kill(user_id)

        killed_player = Player.get(user_id)
        assert not killed_player.alive
        assert killed_player.guessing is expected_guessing

    @staticmethod
    def test_kill_non_existing_player():
        user_id = "1"
        with pytest.raises(Exception):
            Player.kill(user_id)
