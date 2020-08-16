import pytest

from undercover.models import SecretWord


class TestSecretWord:
    @staticmethod
    @pytest.fixture(autouse=True)
    def populate_playing_role(session):
        session.add(SecretWord([]))
        session.add(SecretWord(["word_1"]))
        session.add(SecretWord(["word_1", "word_2"]))
        session.add(SecretWord(["word_1", "word_2", "word_3"]))
        session.commit()
        yield
        session.query(SecretWord).delete()

    @staticmethod
    def test_get_random():
        pass
        secret_word = SecretWord.get_random()
        assert len(secret_word.related_words) > 1
