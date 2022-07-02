import asyncio
import datetime
import logging
import os

import aiohttp
import discord
from discord.ext import commands, tasks

_DNF_API_BASE = "https://api.neople.co.kr/df"

_APP_ID = os.getenv("DNF_API_KEY")


class Dnf(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.channel: discord.TextChannel = None
        self.get_today_grade.start()

    @commands.group(brief="던파 도구")
    async def dnf(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Need subcommand", delete_after=15.0)
            await ctx.message.delete(delay=15.0)

    @dnf.command(brief="오늘의 등급 알림 등록")
    async def sub(self, ctx: commands.Context):
        self.channel = ctx.channel
        message = f"던파 오늘의 등급 알림을 이 채널에 추가함. {self.channel.name}"
        logging.info(message)
        await ctx.send(message)

    @dnf.command(brief="오늘의 등급 알림 등록 해제")
    async def unsub(self, ctx: commands.Context):
        if self.channel is None:
            return
        self.channel = None
        message = "던파 오늘의 등급 알림을 제거함."
        logging.info(message)
        await ctx.send(message)

    @dnf.command(brief="오늘의 등급 확인")
    async def grade(self, ctx: commands.Context):
        await self.get_today_grade()

    @tasks.loop(minutes=1)
    async def get_today_grade(self):
        logging.debug("DNF get_today_grade called")
        # KST 0시 1분에 등급을 알려줌.
        current = datetime.datetime.utcnow()
        if not (current.hour == 15 and current.min == 1):
            return

        if self.channel is None:
            return

        is_status_ok = False
        url = (
            _DNF_API_BASE
            + "/items/ff3bdb021bcf73864005e78316dd961c/shop?apikey="
            + _APP_ID
        )
        RETRY_COUNT = 3
        RETRY_DELAY = 1.0
        async with aiohttp.ClientSession() as session:
            for i in range(RETRY_COUNT):
                async with session.get(url) as response:
                    logging.info("DnF API status : {}".format(response.status))
                    if response.status == 200:
                        is_status_ok = True
                        content = await response.json()
                        grade = content["itemGradeName"]
                        message = "던파 오늘의 등급: " + grade
                        await self.channel.send(message)
                        break
                await asyncio.sleep(RETRY_DELAY)
        if not is_status_ok:
            await self.channel.send("오늘의 등급: 불러오기 실패")

    @get_today_grade.before_loop
    async def before_get_today_grade(self):
        logging.info("DNF scheduler: wait for bot ready")
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    if _APP_ID:
        bot.add_cog(Dnf(bot))
    else:
        logging.warning("Skip to add dnf command")
