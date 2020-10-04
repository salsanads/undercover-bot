class BotPlayerFound(Exception):
    def __init__(self, message=None):
        super().__init__(message or "Bot cannot play the game.")


class MultipleVotesFound(Exception):
    def __init__(self, message="Cannot vote multiple users at once"):
        super().__init__(message)


class EmptyUserArgumentFound(Exception):
    def __init__(self, message="Specify user to vote"):
        super().__init__(message)
