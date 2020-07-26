import os

from dotenv import load_dotenv

import discordbot
import undercover


def main():
    load_dotenv()

    db_url = os.getenv("DB_URL")
    env = os.getenv("ENV")
    undercover.main(db_url, env)

    bot_token = os.getenv("BOT_TOKEN")
    discordbot.main(bot_token)


if __name__ == "__main__":
    main()
