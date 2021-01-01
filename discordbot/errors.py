class BotPlayerFound(Exception):
    def __init__(self, message="Bot cannot play the game"):
        super().__init__(message)


class EmptyVoteFound(Exception):
    def __init__(self, message="Specify user to be voted"):
        super().__init__(message)


class MultipleVotesFound(Exception):
    def __init__(self, message="Cannot vote multiple users at once"):
        super().__init__(message)
