import os

from dotenv import load_dotenv

import discordbot


def main():
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    discordbot.main(bot_token)


if __name__ == "__main__":
    main()
