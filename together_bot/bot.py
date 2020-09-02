import os
import logging
import sys

from dotenv import load_dotenv

import discord
from discord.ext import commands

logging.basicConfig(level=logging.INFO)

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    if message.mentions and bot.user in message.mentions:
        content = message.content.strip()
        mention_prefix = (bot.user.mention, "<@!{}>".format(bot.user.id))
        if content.startswith(mention_prefix):
            len_mention = content.find(">")
            content = message.content[len_mention + 1 :].strip()
            if message.content.startswith("repo"):
                await message.channel.send(
                    "repo URL: https://github.com/team-play-together/together-bot"
                )

    if message.content.startswith("!repo"):
        await message.channel.send(
            "repo URL: https://github.com/team-play-together/together-bot"
        )

    await bot.process_commands(message)


@commands.command()
async def ping(ctx):
    await ctx.send("pong!")


def setup(bot):
    bot.add_command(ping)


def start():
    print("Start bot")
    if DISCORD_BOT_TOKEN:
        setup(bot)
        bot.run(DISCORD_BOT_TOKEN)
    else:
        print("MUST NEED BOT TOKEN", file=sys.stderr)


if __name__ == "__main__":
    start()
