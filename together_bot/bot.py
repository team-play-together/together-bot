import os
import logging
import sys
import random

from dotenv import load_dotenv

import discord
from discord.ext import commands
import together_bot.channel
import together_bot.role

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
            # remains for later

    await bot.process_commands(message)


@bot.event
async def on_member_join(member: discord.Member):
    role_player = discord.utils.get(member.guild.roles, name="player")
    if role_player is None:
        print("Error: Role 'player' doesn't exist.")
        return
    await member.add_roles(role_player)


@commands.command(name="random")
async def _random(ctx, num: int):
    random_number = random.randrange(num) + 1
    await ctx.send(f"Random number : {random_number}")


@commands.command()
async def repo(ctx):
    await ctx.send(
        "Bot repository URL : repo URL: https://github.com/team-play-together/together-bot"
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
    print("Start bot")
    if DISCORD_BOT_TOKEN:
        setup(bot)
        together_bot.channel.setup(bot)
        together_bot.role.setup(bot)
        bot.run(DISCORD_BOT_TOKEN)
    else:
        print("MUST NEED BOT TOKEN", file=sys.stderr)


if __name__ == "__main__":
    start()
