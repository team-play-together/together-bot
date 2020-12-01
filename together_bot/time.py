import logging
import asyncio
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse

import discord
from discord.ext import commands

tz_pst = timezone(-timedelta(hours=8))
tz_kst = timezone(timedelta(hours=9))


class Time(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(brief="시간 관련 명령어 모음")
    async def time(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Need subcommand", delete_after=15.0)
            await ctx.message.delete(delay=15.0)

    @time.command(brief="현재 시간을 UTC와 PST로 보여줌.")
    async def now(self, ctx):
        dt = datetime.now(timezone.utc)
        await ctx.send(
            f"UTC: {dt.isoformat(' ', 'seconds')}\nPST: {dt.astimezone(tz_pst).isoformat(' ', 'seconds')}"
        )

    @time.command(
        brief="입력된 한국 시간을 UTC와 PST로 변환해서 보여줌.",
        help="kst_time에 변환할 한국 기준 시간을 입력(ex.2020-11-30 09:59PM)",
    )
    async def convert(self, ctx, *, kst_time: str):
        try:
            dt = parse(kst_time).astimezone(tz_kst)
            await ctx.send(
                f"UTC: {dt.astimezone(timezone.utc).isoformat(' ', 'seconds')}\nPST: {dt.astimezone(tz_pst).isoformat(' ', 'seconds')}"
            )
        except ValueError:
            logging.error("unknown string format: " + kst_time)
            await ctx.send("unknown string format")
        except OverflowError:
            logging.error("date is too large")
            await ctx.send("date is too large")


def setup(bot):
    bot.add_cog(Time(bot))
