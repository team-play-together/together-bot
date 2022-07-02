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
        self.loop_call_grade.start()

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

    @dnf.command(brief="오늘의 등급 확인 (등록된 채널로 메세지가 전송됨)")
    async def grade(self, ctx: commands.Context):
        if self.channel is None:
            return

        grade = await self._get_grade()
        await self._send_grade(grade)

    @tasks.loop(seconds=10)
    async def loop_call_grade(self):
        logging.debug("DNF loop_call_grade called")
        # KST 0시 0분에 등급을 알려줌.
        current = datetime.datetime.utcnow()
        if not (current.hour == 15 and current.minute == 0):
            return

        if self.channel is None:
            return

        grade = await self._get_grade()
        await self._send_grade(grade)
        await asyncio.sleep(60.0)

    async def __get_grade(self):
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
                        return content["itemGradeName"]
                await asyncio.sleep(RETRY_DELAY)
        if not is_status_ok:
            return None

    async def __send_grade(self, grade):
        if self.channel is None:
            return

        if grade is None:
            await self.channel.send("오늘의 등급: 불러오기 실패")

        message = "던파 오늘의 등급: " + grade
        await self.channel.send(message)

    @loop_call_grade.before_loop
    async def before_get_today_grade(self):
        logging.info("DNF scheduler: wait for bot ready")
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    if _APP_ID:
        bot.add_cog(Dnf(bot))
    else:
        logging.warning("Skip to add dnf command")
