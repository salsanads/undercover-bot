from discord import Colour, Embed
from discord.ext.commands import Cog, command

from discordbot import bot
from discordbot.helpers import command_desc, metadata

from .helpers import register_cog


@register_cog
class Help(Cog):
    @Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} cog ready")

    @command(name="help", description=command_desc.get("HELP"))
    async def handle_help(self, ctx):
        """Displays list of available commands."""
        embed = Embed(title="Commands", color=Colour.blue())
        embed.set_author(
            name=bot.user.name,
            icon_url=bot.user.avatar_url,
            url=metadata.get("BOT_URL"),
        )

        common_commands = []
        guild_only_commands = []
        dm_only_commands = []
        for comm in bot.commands:
            checks_names = list(map(lambda f: f.__qualname__, comm.checks))

            guild_only = (
                list(
                    filter(
                        lambda name: name.startswith("guild_only"),
                        checks_names,
                    )
                )
                != []
            )
            if guild_only:
                guild_only_commands.append(
                    comm.description.format(command_prefix=bot.command_prefix)
                )
                continue

            dm_only = (
                list(
                    filter(
                        lambda name: name.startswith("dm_only"), checks_names
                    )
                )
                != []
            )
            if dm_only:
                dm_only_commands.append(
                    comm.description.format(command_prefix=bot.command_prefix)
                )
                continue

            common_commands.append(
                comm.description.format(command_prefix=bot.command_prefix)
            )

        embed.add_field(
            name="\u200b", value="\n\n".join(common_commands), inline=False,
        )
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(
            name="Channel Only",
            value="\n\n".join(guild_only_commands),
            inline=False,
        )
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(
            name="DM Only", value="\n\n".join(dm_only_commands), inline=False,
        )

        await ctx.send(embed=embed)
