import logging
import logging.config
import os
from pathlib import Path

import discord
import yaml
from discord.ext import commands
from dotenv import load_dotenv

import together_bot.channel
import together_bot.commands
import together_bot.role
import together_bot.time
import together_bot.weather

ROOT_DIR = Path(__file__).parent.parent
CONFIG_PATH = os.path.join(ROOT_DIR, "logging.yml")
with open(CONFIG_PATH) as f:
    logging.config.dictConfig(yaml.safe_load(f))

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)


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


def setup(bot: commands.Bot):
    together_bot.commands.setup(bot)
    together_bot.channel.setup(bot)
    together_bot.role.setup(bot)
    together_bot.time.setup(bot)
    together_bot.weather.setup(bot)


def start():
    logging.info("Start bot")
    if DISCORD_BOT_TOKEN:
        setup(bot)
        bot.run(DISCORD_BOT_TOKEN)
    else:
        logging.error("MUST NEED BOT TOKEN")


if __name__ == "__main__":
    start()
