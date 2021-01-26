import asyncio
import json
import logging
import os
from typing import Optional

import aiohttp
from discord.ext import commands

_OPEN_WEATHER_API_BASE = "https://api.openweathermap.org/data/2.5/"

_APP_ID = os.getenv("OPEN_WEATHER_API_KEY")

_OPEN_WEATHER_API_ENDPOINT = dict(
    map(
        lambda kv: (kv[0], _OPEN_WEATHER_API_BASE + kv[1]),
        {
            "current": "weather",
            "one_call": "onecall",
        }.items(),
    )
)


@commands.group(brief="Show weather")
async def weather(ctx: commands.Context):
    if ctx.invoked_subcommand is None:
        await ctx.send("weather command needs subcommand.")


@weather.command()
async def current(ctx: commands.Context, *, city: Optional[str]):
    async with aiohttp.ClientSession() as session:
        url = _OPEN_WEATHER_API_ENDPOINT["current"]
        query = {
            "appid": _APP_ID,
            "units": "metric",
            "lang": "kr",
        }

        if city is None:
            query |= {"id": "1835848"}
        else:
            query |= {"q": city}

        async with session.get(url, params=query) as response:
            logging.info("Response status : {}".format(response.status))
            if response.status == 200:
                content = await response.text()
                res = json.loads(content)

                name = res["name"]
                weather = res["weather"][0]

                weather_main = weather["main"]
                weather_desc = weather["description"]
                await ctx.send(f"{name} : {weather_main} - {weather_desc}")
            elif response.status == 404:
                await ctx.send(f"{city} is not found.")


def setup(bot: commands.Bot):
    if _APP_ID:
        bot.add_command(weather)
    else:
        logging.warning("Skip to add weather command")


# Use for test
async def _main(app_id: str):
    async with aiohttp.ClientSession() as session:
        url = _OPEN_WEATHER_API_ENDPOINT["current"]
        query = {
            "appid": app_id,
            "units": "metric",
            "lang": "kr",
        }

        query |= {"id": "1835848"}

        async with session.get(url, params=query) as response:
            logging.info("Response status : %s", response.status)
            if response.status == 200:
                content = await response.text()
                res = json.loads(content)

                name = res["name"]
                weather = res["weather"][0]

                weather_main = weather["main"]
                weather_desc = weather["description"]
                print(f"{name} : {weather_main} - {weather_desc}")


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()

    app_id = os.getenv("OPEN_WEATHER_API_KEY")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(app_id))
