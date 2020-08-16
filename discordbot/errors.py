class BotPlayerFound(Exception):
    def __init__(self, message=None):
        super().__init__(message or "Bot cannot play the game.")
