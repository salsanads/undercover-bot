import os

from dotenv import load_dotenv

import discordbot
import undercover


def main():
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    env = os.getenv("ENV")
    undercover.main(database_url, env)

    bot_token = os.getenv("BOT_TOKEN")
    bot_command_prefix = os.getenv("BOT_COMMAND_PREFIX")
    discordbot.main(bot_token, bot_command_prefix)


if __name__ == "__main__":
    main()
