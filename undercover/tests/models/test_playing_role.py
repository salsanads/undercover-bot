import pytest

from undercover import Role
from undercover.models.playing_role import PlayingRole


class TestPlayingRole:
    @staticmethod
    @pytest.fixture(autouse=True)
    def populate_playing_role(session):
        session.add(PlayingRole("1", Role.CIVILIAN.name, "civilian_word"))
        session.add(PlayingRole("1", Role.UNDERCOVER.name, "undercover_word"))
        session.add(PlayingRole("1", Role.MR_WHITE.name))
        session.commit()
        yield
        session.query(PlayingRole).delete()

    @staticmethod
    @pytest.mark.parametrize(
        "room_id, expected_result", [("1", True), ("2", False)]
    )
    def test_exists(room_id, expected_result):
        assert PlayingRole.exists(room_id) is expected_result

    @staticmethod
    def test_insert_word_not_null(session):
        room_id = "2"
        role = Role.CIVILIAN.name
        word = "civilian_word"
        PlayingRole.insert(PlayingRole(room_id, role, word))
        playing_roles = (
            session.query(PlayingRole)
            .filter_by(room_id=room_id, role=role)
            .all()
        )
        assert len(playing_roles) == 1
        playing_role = playing_roles[0]
        assert playing_role.room_id == room_id
        assert playing_role.role == role
        assert playing_role.word == word

    @staticmethod
    def test_insert_word_null(session):
        room_id = "2"
        role = Role.MR_WHITE.name
        PlayingRole.insert(PlayingRole(room_id, role))
        playing_roles = (
            session.query(PlayingRole)
            .filter_by(room_id=room_id, role=role)
            .all()
        )
        assert len(playing_roles) == 1
        playing_role = playing_roles[0]
        assert playing_role.room_id == room_id
        assert playing_role.role == role
        assert playing_role.word is None

    @staticmethod
    def test_insert_duplicate_playing_role():
        room_id = "1"
        role = Role.MR_WHITE.name
        with pytest.raises(Exception):
            PlayingRole.insert(PlayingRole(room_id, role))
