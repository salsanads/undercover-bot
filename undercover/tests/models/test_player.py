import pytest

from undercover import Role
from undercover.models.player import Player, PlayingRole


class TestPlayer:
    @staticmethod
    @pytest.fixture(autouse=True)
    def populate_db(session):
        session.add(PlayingRole("1", Role.CIVILIAN.name, "civilian_word"))
        session.add(PlayingRole("1", Role.UNDERCOVER.name, "undercover_word"))
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

        print(player.playing_role.word)

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
