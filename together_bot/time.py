import logging
from datetime import datetime, timedelta, timezone

import ntplib
from dateutil.parser import ParserError, parse
from discord.ext import commands

tz_pst = timezone(-timedelta(hours=8))
tz_kst = timezone(timedelta(hours=9))
TIME_SERVER = "pool.ntp.org"


class Time(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.ntp_client = ntplib.NTPClient()

    @commands.group(brief="시간 관련 명령어 모음")
    async def time(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Need subcommand", delete_after=15.0)
            await ctx.message.delete(delay=15.0)

    @time.command(brief="현재 시간을 UTC와 PST로 보여줌.")
    async def now(self, ctx: commands.Context):
        try:
            response = self.ntp_client.request(TIME_SERVER, version=3)
            dt = from_utc_timestamp(response.orig_time)
            await ctx.send(
                f"UTC: {to_utc_time_format(dt)}\n"
                + f"PST: {to_pst_time_format(dt)}\n"
                + f"이 정보는 `{TIME_SERVER}` 로부터 제공받았습니다."
            )
        except ntplib.NTPException:
            logging.error("NTP server doesn't respond")
            await ctx.send("NTP 서버에 연결할 수 없습니다. 나중에 다시 시도해주세요.")
        except OverflowError:
            logging.error("Timestamp overflow")
            await ctx.send("잠시 후 다시 시도해주세요.")
        except OSError:
            logging.error("OS can't recognize timestamp")
            await ctx.send("잠시 후 다시 시도해주세요.")

    @time.command(
        brief="입력된 한국 시간을 UTC와 PST로 변환해서 보여줌.",
        help="kst_time에 변환할 한국 기준 시간을 입력(ex.2020-11-30 09:59PM)",
    )
    async def convert(self, ctx: commands.Context, *, kst_time: str):
        try:
            dt = from_kst_time_string(kst_time)
            await ctx.send(
                f"UTC: {to_utc_time_format(dt)}\n" + f"PST: {to_pst_time_format(dt)}"
            )
        except ValueError:
            logging.error("unknown string format: " + kst_time)
            await ctx.send("unknown string format")
        except ParserError:
            logging.error("unknown string format: " + kst_time)
            await ctx.send("unknown string format")
        except TypeError:
            logging.error("wrong type: " + str(type(kst_time)))
            await ctx.send("unknown string format")
        except OSError:
            logging.error("changing timezone failed")
            await ctx.send("convert failed")
        except OverflowError:
            logging.error("date is too large")
            await ctx.send("date is too large")


def from_utc_timestamp(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, timezone.utc)


def to_utc_time_format(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(" ", "seconds")


def to_pst_time_format(dt: datetime) -> str:
    return dt.astimezone(tz_pst).isoformat(" ", "seconds")


def from_kst_time_string(kst_time: str) -> datetime:
    return parse(kst_time, ignoretz=True).replace(tzinfo=tz_kst)


def setup(bot: commands.Bot):
    bot.add_cog(Time(bot))
