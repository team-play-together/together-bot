import asyncio
import sys
from typing import Dict

import discord
from discord.ext import commands


class Role(commands.Cog):
    _raised_hand = "\N{RAISED HAND}"

    def __init__(self, bot):
        self.bot = bot
        self.guild_roles: Dict[int, int] = {}
        self.map_message_role: Dict[int, int] = {}

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        role_player = discord.utils.get(member.guild.roles, name="player")
        if role_player is not None:
            await member.add_roles(role_player)
        else:
            print("Role 'player' doesn't exist.", file=sys.stderr)

    @commands.group()
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Need subcommand")

    @role.command()
    async def create(self, ctx, *, name: str):
        author = ctx.author
        guild = ctx.guild

        if (role := discord.utils.get(guild.roles, name=name)) :
            delay = 15.0
            await ctx.send(f"`{role.name}` is already exists", delete_after=delay)
            await ctx.message.delete(delay=delay)
            return None

        reply = await ctx.send(
            f"To create role '{name}', add {self._raised_hand} reaction"
        )
        await reply.add_reaction(self._raised_hand)

        def check(reaction, user):
            return (
                user == author
                and str(reaction.emoji) == self._raised_hand
                and reaction.message.id == reply.id
            )

        try:
            await ctx.bot.wait_for("reaction_add", check=check, timeout=60.0)
            role = await ctx.guild.create_role(name=name)
            await ctx.send(f"Create role {role.mention}")
        except asyncio.TimeoutError:
            await ctx.send("Timeout: Cancel to create role")
        finally:
            await reply.delete()
            await ctx.message.delete()

    @create.error
    async def create_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("To create : `role create {role}`", delete_after=10.0)
            await ctx.message.delete()

    @role.command()
    async def list(self, ctx):
        pass

    @role.command()
    async def delete(self, ctx, *, name: str):
        pass

    @role.command()
    async def cleanup(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Role(bot))
