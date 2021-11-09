import pytest

from together_bot.fword import (
    FWORD_LIST_PATH,
    Trie,
    TrieNode,
    summarize_fwords,
    to_fwords_set,
)


# Helper function
def find(current_node: TrieNode, value: str):
    for c in value:
        if c not in current_node.child:
            break
        current_node = current_node.child[c]
    return current_node


def is_child(trie: Trie, parent: str, child: str) -> bool:
    if child.find(parent) != 0:
        return False

    if len(child) == len(parent):
        return True

    parent_node = find(trie.root, parent)
    if parent_node.value != parent:
        return False

    child_node = find(parent_node, child[len(parent) :])
    return child_node.value == child


def all_match(expected: list, actual: list):
    return all([x == y for x, y in zip(actual, expected)])


# 1. Trie 테스트
@pytest.fixture
def trie():
    return Trie()


@pytest.fixture
def trie_with_item(trie):
    trie.insert("test")
    return trie


# 1.a. __contains__ 테스트
def test_contains_of_empty_trie(trie):
    # given
    # when
    # then
    assert trie.root.value is None


def test_contains_when_not_str(trie_with_item):
    # given
    # when
    result = 1 in trie_with_item
    # then
    assert not result


def test_contains_when_not_found(trie_with_item):
    # given
    # when
    result = "apple" in trie_with_item
    # then
    assert not result


def test_contains_when_empty_str(trie_with_item):
    # given
    # when
    result = "" in trie_with_item
    # then
    assert not result


def test_contains_when_part_str(trie_with_item):
    # given
    # when
    result = "tes" in trie_with_item
    # then
    assert not result


def test_contains_when_part_str2(trie_with_item):
    # given
    # when
    result = "est" in trie_with_item
    # then
    assert not result


def test_contains_when_part_str3(trie_with_item):
    # given
    # when
    result = "es" in trie_with_item
    # then
    assert not result


def test_contains_when_found(trie_with_item):
    # given
    # when
    result = "test" in trie_with_item
    # then
    assert result


# 1.b. insert test
def test_insert_none(trie):
    # given
    # when and then
    with pytest.raises(TypeError):
        trie.insert(None)


def test_insert_not_str(trie):
    # given
    # when and then
    with pytest.raises(TypeError):
        trie.insert(123)


def test_insert_empty_str(trie):
    # given
    # when
    trie.insert("")
    # then
    assert "" not in trie


def test_insert_single_char(trie):
    # given
    # when
    trie.insert("a")
    # then
    assert "a" in trie


def test_insert_word(trie):
    # given
    # when
    trie.insert("word")
    # then
    assert "word" in trie


def test_insert_not_family(trie):
    # given
    a = "test"
    b = "word"
    # when
    trie.insert(a)
    trie.insert(b)
    # then
    assert a in trie and b in trie
    assert not is_child(trie, a, b) and not is_child(trie, b, a)


def test_insert_not_family2(trie):
    # given
    a = "est"
    b = "test"
    # when
    trie.insert(a)
    trie.insert(b)
    # then
    assert a in trie and b in trie
    assert not is_child(trie, a, b)


def test_insert_family(trie):
    # given
    a = "te"
    b = "test"
    # when
    trie.insert(a)
    trie.insert(b)
    # then
    assert is_child(trie, a, b)


def test_insert_family_reverse(trie):
    # given
    a = "te"
    b = "test"
    # when
    trie.insert(b)
    trie.insert(a)
    # then
    assert is_child(trie, a, b)


def test_insert_family2(trie):
    # given
    a = "te"
    b = "test"
    c = "testword"
    # when
    trie.insert(a)
    trie.insert(b)
    trie.insert(c)
    # then
    assert is_child(trie, a, b) and is_child(trie, a, c) and is_child(trie, b, c)


# 1.c. find_all_occurrences test
def test_find_all(trie):
    # given
    trie.insert("test")
    # when
    actual = trie.find_all_occurrences("This is test sentence")
    # then
    expected = [range(8, 12)]
    assert all_match(expected, actual)


def test_find_all2(trie):
    # given
    trie.insert("test")
    trie.insert("ent")
    # when
    actual = trie.find_all_occurrences("This is test sentence")
    # then
    expected = [range(8, 12), range(14, 17)]
    assert all_match(expected, actual)


def test_find_all_longest_word(trie):
    # given
    trie.insert("test")
    trie.insert("testword")
    # when
    actual = trie.find_all_occurrences("testword is here")
    # then
    expected = [range(0, 8)]
    assert all_match(expected, actual)


def test_find_all_tailing_word(trie):
    # given
    trie.insert("test")
    # when
    actual = trie.find_all_occurrences("This is test")
    # then
    expected = [range(8, 12)]
    assert all_match(expected, actual)


def test_find_all_incomplete_word(trie):
    # given
    trie.insert("thinking")
    # when
    actual = trie.find_all_occurrences("logical think")
    # then
    expected = []
    assert all_match(expected, actual)


def test_ignore_incorrect_but_found_first(trie):
    """
    앞부분이 먼저 검색되지만 뒷부분이 틀린 단어를 무시하고 올바른 단어를 찾을 수 있는지 확인함.
    sentry와 ent라는 단어가 trie에 있을 때,
    this sentence 라는 문장을 필터링하면, sentry의 sent 가 먼저 확인되기 때문에, sentry인지 확인함.
    하지만 sentry 는 포함되지 않는 단어이기 때문에 무시하고 s 뒤에 ent를 찾을 수 있어야 함.
    """
    # given
    trie.insert("sentry")
    trie.insert("ent")
    # when
    actual = trie.find_all_occurrences("this sentence")
    # then
    expected = [range(6, 9)]
    assert all_match(expected, actual)


# 2. fword 명령어 관련 테스트
# 2.a. to_fwords_set() 테스트
def test_occurrences_to_fwords():
    # given
    origin = "안녕 그리고 안녕"
    occurrences = [range(3, 6)]
    # when
    actual = to_fwords_set(origin, occurrences)
    # then
    expected = set(["그리고"])
    assert actual == expected


def test_fwords_without_duplicated():
    # given
    origin = "안녕 그리고 안녕"
    occurrences = [range(0, 2), range(7, 9)]
    # when
    actual = to_fwords_set(origin, occurrences)
    # then
    expected = set(["안녕"])
    assert actual == expected


# 2.b. summarize_fwords() 테스트
def test_empty_summary():
    # given
    detected_fwords = None
    # when
    actual = summarize_fwords(detected_fwords)
    # then
    expected = "없음"
    assert actual == expected


def test_empty_summary2():
    # given
    detected_fwords = []
    # when
    actual = summarize_fwords(detected_fwords)
    # then
    expected = "없음"
    assert actual == expected


def test_summary_less_or_equal_max_represent():
    # given
    max_represent = 3
    detected_fwords = ["하나", "둘"]
    # when
    actual = summarize_fwords(detected_fwords, max_represent)
    # then
    expected = "하나, 둘"
    assert actual == expected


def test_summary_over_max_represent():
    # given
    max_represent = 3
    detected_fwords = ["하나", "둘", "셋", "넷"]
    # when
    actual = summarize_fwords(detected_fwords, max_represent)
    # then
    expected = "하나, 둘, 셋 외 1개"
    assert actual == expected


# 3. 비속어 리스트 테스트
# 테스트에 대한 설명이 PR과 이슈에 적혀있기 때문에 테스트 이름을 번호로 대체함.
# 3.a. 비속어와 비슷하지만 비속어가 아닌 단어 테스트

# 이 Trie는 변경되지 않기 때문에 fixture 대신 변수로 선언.
real_trie = Trie.from_file(FWORD_LIST_PATH)


@pytest.mark.parametrize("non_fword", ["쉐이더 코드", "쉑쉑버거", "쉐이빙폼"])
def test_PR77(non_fword):
    # given
    # when
    actual = real_trie.find_all_occurrences(non_fword)
    # then
    assert len(actual) == 0


@pytest.mark.parametrize("non_fword", ["해야하네", "해야한다", "해야해", "해야해요"])
def test_PR79(non_fword):
    # given
    # when
    actual = real_trie.find_all_occurrences(non_fword)
    # then
    assert len(actual) == 0


def test_PR79_2():
    # given
    # when
    actual = real_trie.find_all_occurrences("난 야하다")
    # then
    expected = [range(2, 5)]
    assert all_match(expected, actual)


@pytest.mark.parametrize("non_fword", ["도망가다", "구라구라꽃"])
def test_PR87(non_fword):
    # given
    # when
    actual = real_trie.find_all_occurrences(non_fword)
    # then
    assert len(actual) == 0


@pytest.mark.parametrize(
    "non_fword", ["그건 진짜지", "이건 좀 극혐이다.", "이건 좀 그켬이다", "이건 좀 극1혐이다"]
)
def test_PR91(non_fword):
    # given
    # when
    actual = real_trie.find_all_occurrences(non_fword)
    # then
    assert len(actual) == 0
