from datetime import datetime, timezone

import pytest

from together_bot.time import (
    from_kst_time_string,
    from_utc_timestamp,
    to_pst_time_format,
    to_utc_time_format,
    tz_kst,
)

kst_time_data = datetime(2020, 11, 30, 21, 59, tzinfo=tz_kst)
utc_time_data = datetime(2020, 11, 30, 21, 59, tzinfo=timezone.utc)


def test_from_utc_timestamp():
    assert from_utc_timestamp(int(1620750422.7079058)) == datetime(
        2021, 5, 11, 16, 27, 2, tzinfo=timezone.utc
    )


@pytest.mark.parametrize(
    "format_test_data, expected",
    [
        (kst_time_data, "2020-11-30 12:59:00+00:00"),
        (utc_time_data, "2020-11-30 21:59:00+00:00"),
    ],
)
def test_to_utc_time_format(format_test_data, expected):
    assert to_utc_time_format(format_test_data) == expected


@pytest.mark.parametrize(
    "format_test_data, expected",
    [
        (kst_time_data, "2020-11-30 04:59:00-08:00"),
        (utc_time_data, "2020-11-30 13:59:00-08:00"),
    ],
)
def test_to_pst_time_format(format_test_data, expected):
    assert to_pst_time_format(format_test_data) == expected


def test_from_kst_time_string():
    assert from_kst_time_string("2020-11-30 09:59PM") == datetime(
        2020, 11, 30, 21, 59, tzinfo=tz_kst
    )


# timezone 정보가 있더라도 입력값은 무조건 KST이라고 간주함.
def test_from_kst_time_string_with_ignoretz():
    assert from_kst_time_string("2021-03-31 17:17:01+00:00") == datetime(
        2021, 3, 31, 17, 17, 1, tzinfo=tz_kst
    )
