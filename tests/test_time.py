from datetime import datetime, timedelta, timezone

import pytest
from dateutil.parser import ParserError

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


@pytest.mark.parametrize(
    "kst_time",
    [
        "10000-02-11 17:48",
        "2021-13-22 12:11",
        "2021-03-32 17:17",
        "2021-02-31",
        "2021-02-28 25:00",
        "2021-03-01 09:70",
    ],
)
def test_kst_time_wrong_date(kst_time):
    with pytest.raises(ValueError):
        from_kst_time_string(kst_time)


@pytest.mark.parametrize(
    "kst_time",
    [
        datetime.min.isoformat(),
        datetime.max.isoformat(),
    ],
)
def test_kst_time_overflow_by_timezone_change(kst_time):
    with pytest.raises(OverflowError):
        dt = from_kst_time_string(kst_time)
        dt.astimezone(timezone(timedelta(hours=8)))  # KST-1
        dt.astimezone(timezone(timedelta(hours=10)))  # KST+1


@pytest.mark.parametrize(
    "kst_time, expected_error",
    [("1523443804214.0", OverflowError), (4.25, TypeError), ("-43201", ParserError)],
)
def test_kst_time_invalid_arguments(kst_time, expected_error):
    with pytest.raises(expected_error):
        from_kst_time_string(kst_time)


@pytest.mark.parametrize(
    "timestamp",
    [
        float("inf"),
        float("-inf"),
    ],
)
def test_timestamp_overflow(timestamp):
    with pytest.raises(OverflowError):
        print(from_utc_timestamp(timestamp))
