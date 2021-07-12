import pytest

from together_bot.fword import Trie, TrieNode, censor


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


# 2. fword 명령어 관련 테스트
# 2.a. censor 테스트


def test_censor_empty_bounds():
    # given
    message = "hello"
    bounds = []
    # when
    actual = censor(message, bounds)
    # then
    expected = "hello"
    assert actual == expected


def test_censor_bounds_only_stop():
    # given
    message = "hello"
    bounds = [range(2)]
    # when
    actual = censor(message, bounds)
    # then
    expected = "||he||llo"
    assert actual == expected


def test_censor_bounds_out_range():
    # given
    message = "hello"
    bounds = [range(-5, -2), range(-1, 3), range(4, 6), range(7, 12)]
    # when
    actual = censor(message, bounds)
    # then
    expected = "hello"
    assert actual == expected


def test_censor():
    # given
    message = "hello"
    bounds = [range(1, 3)]
    # when
    actual = censor(message, bounds)
    # then
    expected = "h||el||lo"
    assert actual == expected
