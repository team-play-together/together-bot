import random

from discord.ext import commands


@commands.command(
    name="random",
    brief="1부터 주어진 수 사이의 임의의 자연수를 출력함.",
    help=(
        "num에 1 이상의 자연수를 넣으면, 1부터 num 사이의 임의의 값을 출력함.\n"
        "그러니까 0 이하의 수나 자연수가 아닌 걸 넣으면 로그 따서 널 XXXXX....)"
    ),
)
async def _random(ctx: commands.Context, num: int):
    random_number = random.randrange(num) + 1
    await ctx.send(f"Random number : {random_number}")


@commands.command(
    brief="together-bot의 repo url을 출력함.",
    help="아니 이 명령어를 help까지 쳐본다고? 그런 당신에게는 role get bot developer",
)
async def repo(ctx: commands.Context):
    await ctx.send(
        "Bot repository URL : https://github.com/team-play-together/together-bot"
    )


@commands.command(brief="구글 검색 결과의 url을 출력함.", help="args에 검색할 내용을 넣으면 됨.")
async def google(ctx: commands.Context, *args):
    query = "+".join(args)
    await ctx.send(f"https://www.google.com/search?q={query}")


@commands.command(
    brief="봇이 탁구를 쳐줍니다. 실행 중이라면 무조건 받아칩니다.",
    help="봇이 실행 중이라면 pong을 출력함.\n(근데 봇이 죽어있으면 help도 안 나오는데 핑을 설명해 줘야해?)",
)
async def ping(ctx: commands.Context):
    await ctx.send("pong!")


@commands.command(brief="together-bot에 기여하는 방법")
async def contribute(ctx: commands.Context):
    await ctx.send(
        "아이디어 제안, 버그 : "
        "`https://github.com/team-play-together/together-bot/issues/new`\n"
        "코드 기여(PR) : `https://github.com/team-play-together/together-bot/pulls`"
    )


def setup(bot: commands.Bot):
    bot.add_command(ping)
    bot.add_command(repo)
    bot.add_command(_random)
    bot.add_command(google)
    bot.add_command(contribute)
