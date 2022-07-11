"""Utility functions."""
from datetime import datetime, timedelta
from typing import NamedTuple

import pytz
from dateutil.relativedelta import relativedelta

from saltapi.web.schema.common import Semester


class TimeInterval(NamedTuple):
    start: datetime
    end: datetime


_partners = dict(
    AMNH="American Museum of Natural History",
    CMU="Carnegie Mellon University",
    DC="Dartmouth College",
    DUR="Durham University",
    GU="Georg-August-Universität Göttingen",
    HET="Hobby Eberly Telescope Board",
    IUCAA="Inter-University Centre for Astronomy & Astrophysics",
    ORP="OPTICON-Radionet Pilot",
    OTH="Other",
    POL="Poland",
    RSA="South Africa",
    RU="Rutgers University",
    UC="University of Canterbury",
    UKSC="UK SALT Consortium",
    UNC="University of North Carolina - Chapel Hill",
    UW="University of Wisconsin-Madison",
)


def partner_name(partner_code: str) -> str:
    """
    Return the partner name for a SALT partner code.
    """

    if partner_code not in _partners:
        raise ValueError(f"Unknown partner code: {partner_code}")

    return _partners[partner_code]


def tonight() -> TimeInterval:
    """
    Return the date interval corresponding to the "night" in which the current time
    lies.

    A night is defined to run from noon to noon.

    For example, for 11 July 2021 11:59:59 "tonight" would be the time interval from
    10 July 2021 12:00:00 to 11 July 2021 12:00. On the other hand, for 11 July 2021
    12:00:01 "tonight" would be the time interval from 11 July 2021 12:00:00 to 12 July
    2021 12:00:00.

    All times are in UTC.
    """
    now = datetime.now(tz=pytz.utc)
    if now.hour < 12:
        now -= timedelta(hours=24)

    start = datetime(now.year, now.month, now.day, 12, 0, 0, 0, tzinfo=pytz.utc)
    end = start + timedelta(hours=24)

    return TimeInterval(start, end)


def semester_start(semester: str) -> datetime:
    """
    Return the start datetime of a semester. The semester must be a string of the
    form "year-semester", such as "2020-2" or "2021-1". Semester 1 of a year starts
    on 1 May noon UTC, semester 2 starts on 1 November noon UTC.

    The returned datetime is in UTC.
    """

    year_str, sem_str = semester.split("-")
    year = int(year_str)
    sem = int(sem_str)
    if sem == 1:
        return datetime(year, 5, 1, 12, 0, 0, 0, tzinfo=pytz.utc)
    if sem == 2:
        return datetime(year, 11, 1, 12, 0, 0, 0, tzinfo=pytz.utc)

    raise ValueError(f"Unknown semester ({sem_str}:  The semester must be 1 or 2.")


def semester_end(semester: str) -> datetime:
    """
    Return the end datetime of a semester. The semester must be a string of the form
    "year-semester", such as "2020-2" or "2021-1". Semester 1 of a year ends on 1
    November noon UTC, semester ends 2 on 1 May noon UTC of the following year.

    The returned datetime is in UTC.
    """

    year_str, sem_str = semester.split("-")
    year = int(year_str)
    sem = int(sem_str)
    if sem == 1:
        return datetime(year, 11, 1, 12, 0, 0, 0, tzinfo=pytz.utc)
    if sem == 2:
        return datetime(year + 1, 5, 1, 12, 0, 0, 0, tzinfo=pytz.utc)

    raise ValueError(f"Unknown semester ({sem_str}:  The semester must be 1 or 2.")


def semester_of_datetime(t: datetime) -> str:
    """
    Return the semester in which a datetime lies.

    The semester is returned as a string of the form "year-semester", such as "2020-2"
    or "2021-1". Semester 1 of a year starts on 1 May noon UTC, semester 2 starts on
    1 November noon UTC.

    The given datetime must be timezone-aware.
    """

    if t.tzinfo is None:
        raise ValueError("The datetime must be timezone-aware")

    shifted = t.astimezone(pytz.utc) - timedelta(hours=12)

    if shifted.month < 5:
        year = shifted.year - 1
        semester = 2
    elif shifted.month < 11:
        year = shifted.year
        semester = 1
    else:
        year = shifted.year
        semester = 2

    return f"{year}-{semester}"


def next_semester() -> str:
    """
    Get the next semester from the current date and time.
    """
    # Adding a month never crosses the month boundary. For example, 31 November plus 6
    # months is 30 April, not 1 May. The semester_of_datetime function takes care of the
    # fact that a semester starts at noon rather than at midnight.
    return Semester(
        semester_of_datetime(datetime.now(tz=pytz.utc) + relativedelta(months=+6))
    )
