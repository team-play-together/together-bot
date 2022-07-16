import asyncio
import datetime
import logging
import os

import aiohttp
import discord
from discord.ext import commands, tasks
from psycopg2 import IntegrityError

from together_bot.models import dnf_grade_channel
from together_bot.utils.db_toolkit import Session

_DNF_API_BASE = "https://api.neople.co.kr/df"

_APP_ID = os.getenv("DNF_API_KEY")


class Dnf(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.channels: set[discord.TextChannel] = set()
        self.today_grade = None
        self.last_etag = None
        self.loop_call_grade.start()

    def cog_unload(self):
        self.loop_call_grade.cancel()
        return super().cog_unload()

    @commands.group(brief="던파 도구")
    async def dnf(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Need subcommand", delete_after=15.0)
            await ctx.message.delete(delay=15.0)

    @dnf.command(brief="오늘의 등급 알림 등록")
    async def sub(self, ctx: commands.Context):
        channel: discord.TextChannel = ctx.channel
        if channel in self.channels:
            logging.debug("이미 등록된 채널")
            return

        try:
            with Session() as session:
                dnf_grade_channel.save(session, channel.id)
                session.commit()
        except IntegrityError as e:
            if "UNIQUE constraint failed: " not in repr(e):
                raise
        self.channels.add(channel)

        message = f"던파 오늘의 등급 알림을 이 채널에 추가함. {channel.name}"
        logging.info(message)
        await ctx.send(message)

    @dnf.command(brief="오늘의 등급 알림 등록 해제")
    async def unsub(self, ctx: commands.Context):
        channel: discord.TextChannel = ctx.channel
        if channel not in self.channels:
            logging.debug("등록되지 않은 채널")
            return

        with Session() as session:
            channel_in_db = dnf_grade_channel.find_by_discord_id(session, channel.id)
            if channel_in_db is not None:
                session.delete(channel_in_db)
                session.commit()
        self.channels.discard(channel)

        message = "던파 오늘의 등급 알림을 제거함."
        logging.info(message)
        await ctx.send(message)

    @dnf.command(brief="오늘의 등급 확인 (등록된 채널로 메세지가 전송됨)")
    async def grade(self, ctx: commands.Context):
        await self.__send_grade(ctx.channel)

    async def __send_grade(self, channel: discord.TextChannel):
        grade_text = self.today_grade if self.today_grade is not None else "갱신되지 않음."
        await channel.send(f"던파 오늘의 등급: {grade_text}")

    @tasks.loop(seconds=10)
    async def loop_call_grade(self):
        logging.debug("DNF loop_call_grade called")
        # KST 0시 0분에 등급을 알려줌.
        current = datetime.datetime.utcnow()
        if not (current.hour == 15 and current.minute == 0):
            return

        updated = await self.__try_update_grade()
        if not updated:
            return

        for channel in self.channels:
            await self.__send_grade(channel)
        await asyncio.sleep(60.0)

    async def __try_update_grade(self):
        url = (
            _DNF_API_BASE
            + "/items/ff3bdb021bcf73864005e78316dd961c/shop?apikey="
            + _APP_ID
        )
        RETRY_COUNT = 3
        RETRY_DELAY = 1.0
        async with aiohttp.ClientSession() as session:
            for _ in range(RETRY_COUNT):
                async with session.get(url) as response:
                    logging.info(f"DnF API status : {response.status}")
                    if response.status == 200:
                        etag = response.headers["etag"]
                        logging.debug("dnf etag: " + etag)
                        if etag == self.last_etag:
                            return False

                        content = await response.json()
                        self.last_etag = etag
                        self.today_grade = content["itemGradeName"]
                        return True
                await asyncio.sleep(RETRY_DELAY)

        return False

    @loop_call_grade.before_loop
    async def before_get_today_grade(self):
        logging.info("DNF scheduler: wait for bot ready")
        await self.bot.wait_until_ready()
        self.__load_channels()
        # 0시 0분과 1분 사이에 등급이 던파 서버에서 갱신되기 직전에 봇이 재시작해버리면
        # 봇이 전날 등급이 최신인줄 알고 알릴 수 있으므로, 루프 전에 etag를 초기화함.
        await self.__try_update_grade()

    @loop_call_grade.after_loop
    async def after_get_today_grade(self):
        logging.info("DNF scheduler: stop loop")

    def __load_channels(self):
        if self.bot is None:
            return

        with Session() as session:
            for (channel_id,) in session.query(
                dnf_grade_channel.DnfGradeChannel.discord_id
            ):
                new_channel = self.bot.get_channel(channel_id)
                self.channels.add(new_channel)
        logging.info(f"dnf subscribed channel count: {len(self.channels)}")


def setup(bot: commands.Bot):
    if _APP_ID:
        bot.add_cog(Dnf(bot))
    else:
        logging.warning("Skip to add dnf command")
