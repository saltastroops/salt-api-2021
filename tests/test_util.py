import freezegun
import pytest
from dateutil.parser import parse

from saltapi.util import (
    TimeInterval,
    next_semester,
    partner_name,
    semester_end,
    semester_of_datetime,
    semester_start,
    tonight,
)


@pytest.mark.parametrize(
    "partner_code,name",
    [
        ("AMNH", "American Museum of Natural History"),
        ("IUCAA", "Inter-University Centre for Astronomy & Astrophysics"),
        ("RSA", "South Africa"),
    ],
)
def test_partner_name_returns_name(partner_code: str, name: str) -> None:
    assert partner_name(partner_code) == name


@pytest.mark.parametrize(
    "now,start,end",
    [
        ("2021-05-19T11:59:59Z", "2021-05-18T12:00:00Z", "2021-05-19T12:00:00Z"),
        ("2021-11-07T12:00:00Z", "2021-11-07T12:00:00Z", "2021-11-08T12:00:00Z"),
        ("2021-10-31T12:00:01Z", "2021-10-31T12:00:00Z", "2021-11-01T12:00:00Z"),
        ("2021-11-07T23:00:00Z", "2021-11-07T12:00:00Z", "2021-11-08T12:00:00Z"),
        ("2021-01-01T01:00:00Z", "2020-12-31T12:00:00Z", "2021-01-01T12:00:00Z"),
    ],
)
def test_tonight(now: str, start: str, end: str) -> None:
    with freezegun.freeze_time(now):
        assert tonight() == TimeInterval(start=parse(start), end=parse(end))


@pytest.mark.parametrize(
    "t,semester",
    [
        ("2022-05-01T11:59:59Z", "2021-2"),
        ("2022-05-01T12:00:00Z", "2022-1"),
        ("2022-05-01T12:00:01Z", "2022-1"),
        ("2021-11-01T11:59:59Z", "2021-1"),
        ("2023-11-01T12:00:00Z", "2023-2"),
        ("2023-11-01T12:00:01Z", "2023-2"),
        ("2022-03-15T07:14:45Z", "2021-2"),
        ("2021-08-09T14:15:56Z", "2021-1"),
        ("2025-12-31T08:16:24Z", "2025-2"),
        ("2020-05-01T13:59:59+02:00", "2019-2"),
        ("2020-05-01T14:01:01+02:00", "2020-1"),
    ],
)
def test_semester_of_datetime_returns_semester(t: str, semester: str) -> None:
    d = parse(t)
    assert semester_of_datetime(d) == semester


def test_semester_of_datetime_requires_utc_datetimes() -> None:
    d = parse("2021-07-14T14:56:13")
    with pytest.raises(ValueError):
        semester_of_datetime(d)


@pytest.mark.parametrize(
    "semester,start",
    [("2019-1", "2019-05-01T12:00:00Z"), ("2021-2", "2021-11-01T12:00:00Z")],
)
def test_semester_start_returns_correct_datetime(semester: str, start: str) -> None:
    d = parse(start)
    assert semester_start(semester) == d


def test_semester_start_raises_error_for_incorrect_semester() -> None:
    with pytest.raises(ValueError):
        semester_start("2021-3")


@pytest.mark.parametrize(
    "semester,end",
    [("2019-1", "2019-11-01T12:00:00Z"), ("2021-2", "2022-05-01T12:00:00Z")],
)
def test_semester_end_returns_correct_datetime(semester: str, end: str) -> None:
    d = parse(end)
    assert semester_end(semester) == d


def test_semester_end_raises_error_for_incorrect_semester() -> None:
    with pytest.raises(ValueError):
        semester_end("2021-3")


@pytest.mark.parametrize(
    "semester,d",
    [
        ("2019-2", "2019-09-05T12:00:00Z"),
        ("2022-1", "2022-02-01T12:00:00Z"),
        ("2022-1", "2022-03-11T12:00:00Z"),
        ("2022-2", "2022-06-23T12:00:00Z"),
        ("2023-1", "2023-04-30T12:00:00Z"),
        # Test if the start of the first semester is correct
        ("2022-1", "2022-05-01T00:00:00Z"),
        ("2022-1", "2022-05-01T11:59:59Z"),
        ("2022-2", "2022-05-01T12:00:00Z"),
        ("2022-2", "2022-05-01T12:00:01Z"),
        # Test if start of the second  semester is correct.
        ("2022-2", "2022-11-01T00:00:01Z"),
        ("2022-2", "2022-11-01T11:59:59Z"),
        ("2023-1", "2022-11-01T12:00:00Z"),
        ("2023-1", "2022-11-01T12:00:01Z"),
        # Test the last date of the start/end semester month
        ("2022-2", "2022-05-31T00:00:00Z"),
        ("2022-2", "2022-05-31T11:59:59Z"),
        ("2022-2", "2022-05-31T12:00:00Z"),
        ("2022-1", "2022-04-30T00:00:01Z"),
        ("2022-1", "2022-04-30T12:00:01Z"),
        ("2022-2", "2022-10-31T00:00:00Z"),
        ("2022-2", "2022-10-31T12:00:00Z"),
        ("2022-2", "2022-10-31T12:00:01Z"),
    ],
)
def test_next_semester_returns_correct_semester(semester: str, d: str) -> None:
    with freezegun.freeze_time(d):
        assert next_semester() == semester
