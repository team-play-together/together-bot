from typing import Dict
import asyncio

from discord.ext import commands

_raised_hand = "\N{RAISED HAND}"


class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_roles: Dict[int, int] = {}
        self.map_message_role: Dict[int, int] = {}

    @commands.group()
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Need subcommand")

    @role.command()
    async def create(self, ctx, *, name: str):
        channel = ctx.channel
        author = ctx.author

        reply = await ctx.send(
            f"To create channel '{name}', add {_raised_hand} reaction"
        )
        await reply.add_reaction(_raised_hand)

        def check(reaction, user):
            return (
                user == ctx.message.author
                and str(reaction.emoji) == _raised_hand
                and reaction.message.id == reply.id
            )

        try:
            await ctx.bot.wait_for("reaction_add", check=check, timeout=60.0)
            role = await ctx.guild.create_role(name=name)
            await ctx.send(f"Create role @{role.mention}")
        except asyncio.TimeoutError:
            await reply.delete()
            await ctx.message.delete()

    @role.command()
    async def delete(self, ctx, *, name: str):
        pass

    @role.command()
    async def cleanup(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Role(bot))
