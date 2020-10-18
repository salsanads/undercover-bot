from discordbot import bot


def register_cog(cog_cls):
    bot.add_cog(cog_cls(bot))
