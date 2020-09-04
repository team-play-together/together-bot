import os
import logging
import sys

from dotenv import load_dotenv

import discord
from discord.ext import commands

logging.basicConfig(level=logging.INFO)

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

client = discord.Client()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if message.mentions and client.user in message.mentions:
        content = message.content.strip()
        mention_prefix = (client.user.mention, "<@!{}>".format(client.user.id))
        if content.startswith(mention_prefix):
            len_mention = content.find(">")
            content = message.content[len_mention + 1 :].strip()
            if content.startswith("ping"):
                await message.channel.send("pong")
            elif message.content.startswith("repo"):
                await message.channel.send(
                    "repo URL: https://github.com/team-play-together/together-bot"
                )

    if message.content.startswith("!ping"):
        await message.channel.send("pong")
    elif message.content.startswith("!repo"):
        await message.channel.send(
            "repo URL: https://github.com/team-play-together/together-bot"
        )


def start():
    print("Start bot")
    if DISCORD_BOT_TOKEN:
        client.run(DISCORD_BOT_TOKEN)
    else:
        print("MUST NEED BOT TOKEN", file=sys.stderr)


if __name__ == "__main__":
    start()
