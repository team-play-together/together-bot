import logging
import logging.config
import os
import random
import sys
from pathlib import Path

import yaml
import discord
from discord.ext import commands
from dotenv import load_dotenv

import together_bot.channel
import together_bot.role

ROOT_DIR = Path(__file__).parent.parent
CONFIG_PATH = os.path.join(ROOT_DIR, "logging.yml")
with open(CONFIG_PATH) as f:
    logging.config.dictConfig(yaml.safe_load(f))

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))


@bot.event
async def on_ready():
    logging.info(f"We have logged in as {bot.user}")


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
            # remains for later

    await bot.process_commands(message)


@commands.command(name="random")
async def _random(ctx, num: int):
    random_number = random.randrange(num) + 1
    await ctx.send(f"Random number : {random_number}")


@commands.command()
async def repo(ctx):
    await ctx.send(
        "Bot repository URL : https://github.com/team-play-together/together-bot"
    )


@commands.command()
async def google(ctx, *args):
    query = "+".join(args)
    await ctx.send(f"https://www.google.com/search?q={query}")


@commands.command()
async def ping(ctx):
    await ctx.send("pong!")


def setup(bot):
    bot.add_command(ping)
    bot.add_command(repo)
    bot.add_command(_random)
    bot.add_command(google)


def start():
    logging.info("Start bot")
    if DISCORD_BOT_TOKEN:
        setup(bot)
        together_bot.channel.setup(bot)
        together_bot.role.setup(bot)
        bot.run(DISCORD_BOT_TOKEN)
    else:
        logging.error("MUST NEED BOT TOKEN")


if __name__ == "__main__":
    start()
