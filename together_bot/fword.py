import csv
import logging
import os
import time
from typing import Iterable

import discord
from discord.ext import commands

FWORD_LIST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fword_list.csv")
)


# 원래는 컨벤션에 따라 f랑 word를 구분해야 하지만 명령어에서 구분하지 않기 때문에 일관성을 위해 코드에서도 구분하지 않음.
class Fword(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.target_user_ids: set[int] = set()
        self.__load_words_file(FWORD_LIST_PATH)

    @commands.group(brief="비속어 탐지기")
    async def fword(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Need subcommand", delete_after=15.0)
            await ctx.message.delete(delay=15.0)

    @fword.command(brief="자신의 메세지에 대한 감시를 켜고 끔", help="is_on에 on 또는 off 입력")
    async def watch(self, ctx: commands.Context, is_on: str):
        is_on = is_on.lower()
        author_id = ctx.author.id
        author_display_name = ctx.author.display_name
        if is_on == "on":
            self.target_user_ids.add(author_id)
            await ctx.send(f"`{author_display_name}`에 대한 비속어 탐지 켜짐")
        elif is_on == "off":
            self.target_user_ids.discard(author_id)
            await ctx.send(f"`{author_display_name}`에 대한 비속어 탐지 꺼짐")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.author.id not in self.target_user_ids:
            return

        # 비속어 탐지
        ctx = await self.bot.get_context(message)
        if not ctx.valid:
            origin = message.content
            occurrences = self.search_tree.find_all_occurrences(origin)
            if len(occurrences) == 0:
                return
            censored = self.__censor(origin, occurrences)
            await message.delete()
            await message.channel.send(f"{message.author.display_name}: {censored}")

    def __censor(self, content: str, bounds: Iterable[tuple[int, int]]):
        # bounds 안의 범위들은 반드시 [n,m) 이고, n <= m 임.
        def check(lower: int, upper: int):
            # 0 <= lower < upper <= len(content)
            return lower >= 0 and lower < upper and upper <= len(content)

        char_list = [*content]
        for bound in bounds:
            lower = bound[0]
            upper = bound[1]
            if check(lower, upper):
                char_list[lower:upper] = ["\\*"] * (upper - lower)

        return "".join(char_list)

    def __load_words_file(self, file_path: str):
        self.search_tree = Trie()
        timestamp_load_begin = time.process_time()
        with open(file_path, newline="", encoding="utf-8") as file:
            csv_reader = csv.reader(file, skipinitialspace=True)
            for row in csv_reader:
                for col in row:
                    self.search_tree.insert(col)
        elapsed_time = time.process_time() - timestamp_load_begin
        logging.info(f"fword list load - elapsed time: {elapsed_time}")


def setup(bot: commands.Bot):
    if os.path.exists(FWORD_LIST_PATH):
        bot.add_cog(Fword(bot))
    else:
        logging.warning("Skip to add fword command")


class TrieNode:
    def __init__(self, value: str):
        self.value: str = value
        self.child: dict[str, TrieNode] = {}


class Trie:
    def __init__(self):
        self.root: TrieNode = TrieNode(None)

    def insert(self, new_value: str):
        # 1. 루트에서 첫 글자부터 하나씩 아래로 노드를 만들면서 맨 끝 글자에 문자열을 삽입한다.
        # 2. 만약 다음에 읽을 글자에 상관없이 해당 문자열이 유일하면 더 이상 아래로 내려가지 않는다.
        # 3. 만약 2번 조건에 의해 자신의 문자 개수보다 윗 노드에 저장된 문자열과 새로 삽입될 문자열이 충돌한다면 아래로 내려서 분기시킨다.
        if not isinstance(new_value, str):
            return

        if len(new_value) == 0:
            return

        # empty string을 가리키는 root부터 시작
        current_node = self.root

        for index in range(0, len(new_value)):
            char = new_value[index]
            # 만약 현재 글자에 해당되는 자식이 없다면, 2번 조건이 만족되는 위치다. 따라서 이 노드가 3번 조건에 해당되는지 확인한다.
            if char not in current_node.child:
                current_node.child[char] = TrieNode(None)

                value = current_node.value
                # 기존 문자열이 없거나 기존 문자열이 1번 조건만 만족한다면, 2번 조건에 의해 삽입함.
                if value is None:
                    current_node = current_node.child[char]
                    break
                if len(value) == index:
                    current_node = current_node.child[char]
                    break

                # 만약 현재 노드가 2번 조건에 의해 생성되었던 노드라면 3번 조건에 해당하므로 분기점을 찾을 때까지 내려보낸다.
                current_node.value = None
                if value[index] != char:
                    current_node.child[value[index]] = TrieNode(value)
                else:
                    current_node.child[char].value = value

            current_node = current_node.child[char]

        # 만약 위 루프에서 문자열을 끝까지 읽은 후의 노드가 2번 조건에 의해 생성되었다면, 자식 노드로 옮김.
        old_value = current_node.value
        if old_value is not None:
            if len(old_value) > len(new_value):
                current_node.child[old_value[len(new_value)]] = TrieNode(old_value)
        # 새 문자열 삽입
        current_node.value = new_value

    def __contains__(self, value: str):
        if self.root is None:
            return False

        if isinstance(value, str):
            current_node = self.root
            for c in value:
                if c not in current_node.child:
                    break
                current_node = current_node.child[c]
            return current_node.value == value
        return False

    def find_all_occurrences(self, sentence: str):
        occurrences: list[tuple[int, int]] = []
        if sentence is None:
            return None

        sentence = sentence.casefold()
        substr_start = 0
        while substr_start < len(sentence):
            # 부분 문자열을 읽으면서 가장 비슷한 비속어를 탐색함.
            index = substr_start
            current_node = self.root
            while index < len(sentence):
                c = sentence[index]
                if c not in current_node.child:
                    break

                current_node = current_node.child[c]
                index += 1

            # 만약 일치하면 단어 범위를 리스트에 추가 후 그 다음부터 재탐색
            # 아니면 시작지점에서 한 칸 전진하고 재탐색
            match = current_node.value
            if match is not None:
                substr_end = substr_start + len(match)
                if sentence[substr_start:substr_end] == match:
                    occurrences.append((substr_start, substr_end))
                    substr_start = substr_end
                    continue
            substr_start = substr_start + 1

        return occurrences
