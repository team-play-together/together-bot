import asyncio

from discord.ext import commands


@commands.group()
async def channel(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Need subcommand")


@channel.command()
async def create(ctx, *, name: str):
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


def setup(bot):
    bot.add_command(channel)
