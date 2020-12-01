import logging
import asyncio
from typing import Dict, Optional
import re

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

    @commands.group(brief="역할 관련 명령어 모음.")
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Need subcommand", delete_after=15.0)
            await ctx.message.delete(delay=15.0)

    @role.command(brief="특정 역할에 참가함.", help="name에 참가할 역할 이름을 입력함.")
    async def get(self, ctx, name: str, duration: Optional[str]):
        logging.info(f"Call get commands with name: `{name}`, duration: `{duration}`")

        def convert_to_seconds(time_duration: str):
            seconds_per_unit = {
                "s": 1.0,
                "m": 60.0,
                "h": 60.0 * 60,
                "d": 60.0 * 60 * 24,
                "w": 60.0 * 60 * 24 * 7,
            }

            return int(time_duration[:-1]) * seconds_per_unit[time_duration[-1]]

        delay = 60.0 * 10
        role = discord.utils.get(ctx.guild.roles, name=name)

        if duration is not None:
            duration = duration.strip().lower()
            r = re.compile(r"^[0-9]+[smhdw]$")
            if r.match(duration):
                two_week_seconds = convert_to_seconds("2w")

                delay = convert_to_seconds(duration)

                if delay > two_week_seconds:
                    delay = two_week_seconds

        logging.info(f"`Get` command sets delay: {delay}")

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

            await ctx.message.delete(delay=delay)

    @get.error
    async def get_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("`role get {role}`, role name must need", delete_after=10.0)
            await ctx.message.delete()

    @role.command(brief="역할을 생성함.", help="name에 생성할 역할의 이름을 입력함.")
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

    @role.command(brief="TBD")
    async def list(self, ctx):
        pass

    @role.command(brief="TBD")
    async def delete(self, ctx, *, name: str):
        pass

    @role.command(brief="TBD")
    async def cleanup(self, ctx):
        pass

    @role.command(brief="특정 역할에 속한 사람들의 이름을 전부 출력함.", help="name에 보고 싶은 역할의 이름을 입력함.")
    async def members(self, ctx, name: str):
        logging.info(f"Call members commands with name: `{name}`")
        guild = ctx.guild

        if (role := discord.utils.get(guild.roles, name=name)) :
            if len(role.members) == 0:
                await ctx.send(f"No one is in role `{role.name}`.")
                return None
            member_names = ", ".join([f"`{member.name}`" for member in role.members])
            await ctx.send(f"Members of `{role.name}`: {member_names}")

    @members.error
    async def members_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "To list members of the role : `role members {role}`", delete_after=10.0
            )
            await ctx.message.delete()


def setup(bot):
    bot.add_cog(Role(bot))
