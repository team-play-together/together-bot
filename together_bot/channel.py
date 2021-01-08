import asyncio

from discord.ext import commands


@commands.group(brief="TBD")
async def channel(ctx: commands.Context):
    if ctx.invoked_subcommand is None:
        await ctx.send("Need subcommand")


@channel.command(brief="TBD")
async def create(ctx: commands.Context, *, name: str):
    # text channel format : no space, use `-`
    # voice channel name : can include space
    channel = ctx.channel

    def check(m):
        return m.channel == channel

    try:
        await ctx.bot.wait_for("message", check=check, timeout=60.0)
        await ctx.send("subcommand test")
    except asyncio.TimeoutError:
        await ctx.message.delete()


def setup(bot: commands.Bot):
    bot.add_command(channel)
