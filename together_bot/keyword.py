import discord
from discord.ext import commands


class Keyword(commands.Cog):
    MAX_KEYWORD = 10
    MAX_KEYWORD_LENGTH = 20
    MAX_TARGET_LENGTH = 1000

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.userDict = {}
        self.keywordDict = {}

    @commands.group(
        brief="사용자가 특정 키워드를 입력했을 때 봇이 자신을 mention하게 등록",
        help="자신에게 등록할 키워드를 설정하는 명령어입니다",
    )
    async def keyword(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("자세한 명령어는 `help keyword`")

    @keyword.command(brief="자신의 키워드에 KEYWORD를 등록합니다.", help="`!keyword add KEYWORD`")
    async def add(self, ctx: commands.Context, keyword: str):
        # 등록 가능한 키워드의 길이가 MAX_KEYWORD_LENGTH(20)을 초과할 경우 등록할 수 없게 제한
        if len(keyword) > Keyword.MAX_KEYWORD_LENGTH:
            await ctx.send(f"길이가 {Keyword.MAX_KEYWORD_LENGTH} 초과인 키워드는 등록할 수 없습니다.")
            return

        keywordsByUserID = self.getKeywordsByUserID(ctx.author.id)
        # 한 사용자당 MAX_KEYWORD(10개)이상의 키워드는 등록할 수 없게 제한
        if len(keywordsByUserID) >= Keyword.MAX_KEYWORD:
            await ctx.send(
                f"`{ctx.author.display_name}` 사용자의 keyword 개수가 "
                f"{Keyword.MAX_KEYWORD}개 이상이어서 추가로 등록할 수 없습니다."
            )
            return
        # 중복 키워드가 없을 경우 키워드 등록
        if keyword not in keywordsByUserID:
            self.addToDict(ctx.author.id, keyword)
            await ctx.send(
                f"`{ctx.author.display_name}` 사용자의 Keyword 리스트에 "
                f"`{keyword}`가 추가되었습니다."
            )
        else:
            await ctx.send(
                f"`{ctx.author.display_name}` 사용자의 Keyword 리스트에 "
                f"`{keyword}`가 이미 있습니다."
            )

    @keyword.command(
        brief="자신에게 등록된 키워드 중 KEYWORD를 삭제합니다.", help="`!keyword delete KEYWORD`"
    )
    async def delete(self, ctx: commands.Context, keyword: str):
        keywordsByUserID = self.getKeywordsByUserID(ctx.author.id)
        if keyword not in keywordsByUserID:
            await ctx.send(
                f"`{ctx.author.display_name}` 사용자의 Keyword 리스트에 "
                f"`{keyword}`가 존재하지 않습니다."
            )
        else:
            self.deleteFromDict(ctx.author.id, keyword)
            await ctx.send(
                f"`{ctx.author.display_name}` 사용자의 Keyword 리스트에서 "
                f"`{keyword}`가 제거되었습니다."
            )

    def addToDict(self, userID, keyword):
        keywordsByUserID = self.getKeywordsByUserID(userID)
        keywordsByUserID.add(keyword)
        usersBykeyword = self.getUsersByKeyword(keyword)
        usersBykeyword.add(userID)

    def deleteFromDict(self, userID, keyword):
        keywordsByUserID = self.getKeywordsByUserID(userID)
        keywordsByUserID.remove(keyword)
        usersBykeyword = self.getUsersByKeyword(keyword)
        usersBykeyword.remove(userID)

    def getKeywordsByUserID(self, userID):
        if userID not in self.userDict:
            self.userDict[userID] = set()
        return self.userDict[userID]

    def getUsersByKeyword(self, keyword):
        if keyword not in self.keywordDict:
            self.keywordDict[keyword] = set()
        return self.keywordDict[keyword]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 봇 관련 채팅은 무시
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return
        if message.author.bot:
            return
        # 키워드가 아무것도 등록되어 있지 않을 경우 무시
        if not self.userDict or not self.keywordDict:
            return
        # 채팅 문자열의 길이가MAX_TARGET_LENGTH 이상일 경우 무시
        if len(message.content) > Keyword.MAX_TARGET_LENGTH:
            return

        mentions = list()
        # 입력된 메시지와 등록된 키워드를 확인하며 mention할 유저가 있는지 확인함
        for keyword in self.keywordDict:
            if self.getUsersByKeyword(keyword) and Keyword.kmp(
                message.content, keyword
            ):
                mentions.append(
                    {"keyword": keyword, "userIDs": self.getUsersByKeyword(keyword)}
                )

        if not mentions:
            return

        mentionText = str()
        for mention in mentions:
            mentionText += f"`{mention['keyword']}` 키워드에 의해 호출됨: "
            userMentionFormat = list()
            for userID in mention["userIDs"]:
                # discord의 유저 mention 형태로 유저 ID를 포맷함: ex) <@12312312312312312>
                userMentionFormat.append(f"<@{userID}> ")
            mentionText += ", ".join(userMentionFormat) + "\n"
        await message.channel.send(mentionText)

    # target 문자열 안에key 문자열의  존재 여부를 boolean으로 리턴함
    def kmp(target: str, key: str):
        if len(target) < len(key):
            return False
        pi = Keyword.getPi(key)
        i = 0
        j = 0
        while i < len(target):
            if target[i] == key[j]:
                i += 1
                j += 1
            # 문자가 맞지 않을 경우 pi배열의 값을 참고하여 재탐색
            else:
                if j == 0:
                    i += 1
                else:
                    j = pi[j - 1]

            if j == len(key):
                return True
        return False

    # key 문자열의 pi 배열을 리턴함
    def getPi(key: str):
        pi = [0] * len(key)
        i = 1
        prefix = 0  # prefix의 최대 길이

        while i < len(key):
            # 문자가 같을 경우: 이전 prifix의 최대값 길이 + 1
            if key[i] == key[prefix]:
                prefix += 1
                pi[i] = prefix
                i += 1
            # 문자가 다른 경우
            else:
                # 같은 prefix가 없는 경우: prefix 길이 0으로 줄이고 다음 인덱스로 넘어감
                if prefix == 0:
                    i += 1
                # 같은 prefix가 있는 경우: prefix 길이 1 줄이고 재검사
                else:
                    prefix = pi[prefix - 1]
        return pi


def setup(bot: commands.Bot):
    bot.add_cog(Keyword(bot))
