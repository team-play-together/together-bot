import logging
import asyncio
import sys
from typing import Dict

import discord
from discord.ext import commands


class Role(commands.Cog):
    _raised_hand = "\N{RAISED HAND}"

    def __init__(self, bot):
        self.bot = bot
        self.guild_message_role: Dict[discord.Guild, Dict[int, discord.Role]] = {}

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        role_player = discord.utils.get(member.guild.roles, name="player")
        if role_player is not None:
            await member.add_roles(role_player)
        else:
            logging.error("Role 'player' doesn't exist.")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user.bot is True:
            return

        if reaction.message.guild is not None:
            if (message_role := self.guild_message_role.get(reaction.message.guild)) :
                if (role := message_role.get(reaction.message.id)) :
                    await user.add_roles(role)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User):
        if user.bot is True:
            return

        if reaction.message.guild is not None:
            if (message_role := self.guild_message_role.get(reaction.message.guild)) :
                if (role := message_role.get(reaction.message.id)) :
                    await user.remove_roles(role)

    @commands.group()
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Need subcommand", delete_after=15.0)
            await ctx.message.delete(delete_after=15.0)

    @role.command()
    async def get(self, ctx, name: str):
        delay = 60.0 * 5
        role = discord.utils.get(ctx.guild.roles, name=name)
        if role is not None:
            message = await ctx.send(
                f"Exists **_{role.name}_**, assign to role, "
                f"add Reaction {self._raised_hand}",
                delete_after=delay,
            )
            await message.add_reaction(self._raised_hand)

            if self.guild_message_role.get(ctx.guild) is None:
                self.guild_message_role[ctx.guild] = {}
            self.guild_message_role[ctx.guild][message.id] = role

            ctx.message.delete(delay=delay)

    @get.error
    async def get_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("`role get {role}`, role name must need", delete_after=10.0)
            await ctx.message.delete()

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
