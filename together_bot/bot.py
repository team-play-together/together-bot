import os
import logging
from dotenv import load_dotenv

import discord
from discord.ext import commands

logging.basicConfig(level=logging.INFO)

load_dotenv(verbose=True)

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if message.mentions:
        # TODO: reaction only mentions
        # BOT mention text: `<@!749558517685551166>`
        pass
    if message.content.startswith('!ping'):
        await message.channel.send('pong')

def start():
    client.run(DISCORD_BOT_TOKEN)

