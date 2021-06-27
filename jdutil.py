"""
Functions for converting dates to/from JD and MJD. Assumes dates are historical
dates, including the transition from the Julian calendar to the Gregorian
calendar in 1582. No support for proleptic Gregorian/Julian calendars.

:Author: Matt Davis
:Website: http://github.com/jiffyclub

see http://en.wikipedia.org/wiki/Julian_day

"""

import math
import datetime as dt
import pytz

# Note: The Python datetime module assumes an infinitely valid Gregorian calendar.
#       The Gregorian calendar took effect after 10-15-1582 and the dates 10-05 through
#       10-14-1582 never occurred. Python datetime objects will produce incorrect
#       time deltas if one date is from before 10-15-1582.

# AW 2014-01-24
#


def dt2mjd(dtlist):
    """
    convert list of datetimes to list of MJDs
    """
    mjdlist = []
    for d in dtlist:
        mjdlist.append(jd_to_mjd(datetime_to_jd(d)))
    return mjdlist


def datetime_to_mjd(dt):
    return jd_to_mjd(datetime_to_jd(dt))


def stamp2dt(stamplist):
    """
    convert list of time-stamps to list of datetimes
    """
    dtlist = []
    for t in stamplist:
        dtlist.append(datetime.fromtimestamp(t, tz=pytz.UTC))
    return dtlist


def mjd_to_datetime(mjd):
    """
    convert mjd to datetime
    """
    return jd_to_datetime(mjd_to_jd(mjd))


def mjd_to_jd(mjd):
    """
    Convert Modified Julian Day to Julian Day.

    Parameters
    ----------
    mjd : float
        Modified Julian Day

    Returns
    -------
    jd : float
        Julian Day


    """
    return mjd + 2400000.5


def jd_to_mjd(jd):
    """
    Convert Julian Day to Modified Julian Day

    Parameters
    ----------
    jd : float
        Julian Day

    Returns
    -------
    mjd : float
        Modified Julian Day

    """
    return jd - 2400000.5


def date_to_jd(year, month, day):
    """
    Convert a date to Julian Day.

    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet', 
        4th ed., Duffet-Smith and Zwart, 2011.

    Parameters
    ----------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.

    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.

    day : float
        Day, may contain fractional part.

    Returns
    -------
    jd : float
        Julian Day

    Examples
    --------
    Convert 6 a.m., February 17, 1985 to Julian Day

    >>> date_to_jd(1985,2,17.25)
    2446113.75

    """
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month

    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if ((year < 1582) or
        (year == 1582 and month < 10) or
            (year == 1582 and month == 10 and day < 15)):
        # before start of Gregorian calendar
        B = 0
    else:
        # after start of Gregorian calendar
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)

    if yearp < 0:
        C = math.trunc((365.25 * yearp) - 0.75)
    else:
        C = math.trunc(365.25 * yearp)

    D = math.trunc(30.6001 * (monthp + 1))

    jd = B + C + D + day + 1720994.5

    return jd


def jd_to_date(jd):
    """
    Convert Julian Day to date.

    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet', 
        4th ed., Duffet-Smith and Zwart, 2011.

    Parameters
    ----------
    jd : float
        Julian Day

    Returns
    -------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.

    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.

    day : float
        Day, may contain fractional part.

    Examples
    --------
    Convert Julian Day 2446113.75 to year, month, and day.

    >>> jd_to_date(2446113.75)
    (1985, 2, 17.25)

    """
    jd = jd + 0.5

    F, I = math.modf(jd)
    I = int(I)

    A = math.trunc((I - 1867216.25)/36524.25)

    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I

    C = B + 1524

    D = math.trunc((C - 122.1) / 365.25)

    E = math.trunc(365.25 * D)

    G = math.trunc((C - E) / 30.6001)

    day = C - E + F - math.trunc(30.6001 * G)

    if G < 13.5:
        month = G - 1
    else:
        month = G - 13

    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715

    return year, month, day


def hmsm_to_days(hour=0, min=0, sec=0, micro=0):
    """
    Convert hours, minutes, seconds, and microseconds to fractional days.

    Parameters
    ----------
    hour : int, optional
        Hour number. Defaults to 0.

    min : int, optional
        Minute number. Defaults to 0.

    sec : int, optional
        Second number. Defaults to 0.

    micro : int, optional
        Microsecond number. Defaults to 0.

    Returns
    -------
    days : float
        Fractional days.

    Examples
    --------
    >>> hmsm_to_days(hour=6)
    0.25

    """
    days = sec + (micro / 1.e6)

    days = min + (days / 60.)

    days = hour + (days / 60.)

    return days / 24.


def days_to_hmsm(days):
    """
    Convert fractional days to hours, minutes, seconds, and microseconds.
    Precision beyond microseconds is rounded to the nearest microsecond.

    Parameters
    ----------
    days : float
        A fractional number of days. Must be less than 1.

    Returns
    -------
    hour : int
        Hour number.

    min : int
        Minute number.

    sec : int
        Second number.

    micro : int
        Microsecond number.

    Raises
    ------
    ValueError
        If `days` is >= 1.

    Examples
    --------
    >>> days_to_hmsm(0.1)
    (2, 24, 0, 0)

    """
    hours = days * 24.
    hours, hour = math.modf(hours)

    mins = hours * 60.
    mins, min = math.modf(mins)

    secs = mins * 60.
    secs, sec = math.modf(secs)

    micro = round(secs * 1.e6)

    return int(hour), int(min), int(sec), int(micro)


def datetime_to_jd(date):
    """
    Convert a `datetime.datetime` object to Julian Day.

    Parameters
    ----------
    date : `datetime.datetime` instance

    Returns
    -------
    jd : float
        Julian day.

    Examples
    --------
    >>> d = datetime.datetime(1985,2,17,6)  
    >>> d
    datetime.datetime(1985, 2, 17, 6, 0)
    >>> jdutil.datetime_to_jd(d)
    2446113.75

    """
    days = date.day + \
        hmsm_to_days(date.hour, date.minute, date.second, date.microsecond)

    return date_to_jd(date.year, date.month, days)


def jd_to_datetime(jd):
    """
    Convert a Julian Day to an `jdutil.datetime` object.

    Parameters
    ----------
    jd : float
        Julian day.

    Returns
    -------
    dt : `jdutil.datetime` object
        `jdutil.datetime` equivalent of Julian day.

    Examples
    --------
    >>> jd_to_datetime(2446113.75)
    datetime(1985, 2, 17, 6, 0)

    """
    year, month, day = jd_to_date(jd)

    frac_days, day = math.modf(day)
    day = int(day)

    hour, min, sec, micro = days_to_hmsm(frac_days)

    return datetime(year, month, day, hour, min, sec, micro)


def timedelta_to_days(td):
    """
    Convert a `datetime.timedelta` object to a total number of days.

    Parameters
    ----------
    td : `datetime.timedelta` instance

    Returns
    -------
    days : float
        Total number of days in the `datetime.timedelta` object.

    Examples
    --------
    >>> td = datetime.timedelta(4.5)
    >>> td
    datetime.timedelta(4, 43200)
    >>> timedelta_to_days(td)
    4.5

    """
    seconds_in_day = 24. * 3600.

    days = td.days + (td.seconds + (td.microseconds * 10.e6)) / seconds_in_day

    return days


class datetime(dt.datetime):
    """
    A subclass of `datetime.datetime` that performs math operations by first
    converting to Julian Day, then back to a `jdutil.datetime` object.

    Addition works with `datetime.timedelta` objects, subtraction works with
    `datetime.timedelta`, `datetime.datetime`, and `jdutil.datetime` objects.
    Not all combinations work in all directions, e.g.
    `timedelta - datetime` is meaningless.

    See Also
    --------
    datetime.datetime : Parent class.

    """

    def __add__(self, other):
        if not isinstance(other, dt.timedelta):
            s = "jdutil.datetime supports '+' only with datetime.timedelta"
            raise TypeError(s)

        days = timedelta_to_days(other)

        combined = datetime_to_jd(self) + days

        return jd_to_datetime(combined)

    def __radd__(self, other):
        if not isinstance(other, dt.timedelta):
            s = "jdutil.datetime supports '+' only with datetime.timedelta"
            raise TypeError(s)

        days = timedelta_to_days(other)

        combined = datetime_to_jd(self) + days

        return jd_to_datetime(combined)

    def __sub__(self, other):
        if isinstance(other, dt.timedelta):
            days = timedelta_to_days(other)

            combined = datetime_to_jd(self) - days

            return jd_to_datetime(combined)

        elif isinstance(other, (datetime, dt.datetime)):
            diff = datetime_to_jd(self) - datetime_to_jd(other)

            return dt.timedelta(diff)

        else:
            s = "jdutil.datetime supports '-' with: "
            s += "datetime.timedelta, jdutil.datetime and datetime.datetime"
            raise TypeError(s)

    def __rsub__(self, other):
        if not isinstance(other, (datetime, dt.datetime)):
            s = "jdutil.datetime supports '-' with: "
            s += "jdutil.datetime and datetime.datetime"
            raise TypeError(s)

        diff = datetime_to_jd(other) - datetime_to_jd(self)

        return dt.timedelta(diff)

    def to_jd(self):
        """
        Return the date converted to Julian Day.

        """
        return datetime_to_jd(self)

    def to_mjd(self):
        """
        Return the date converted to Modified Julian Day.

        """
        return jd_to_mjd(self.to_jd())


def mjdnow():
    return jd_to_mjd(datetime_to_jd(dt.datetime.utcnow()))


if __name__ == "__main__":
    print("Local time: ", dt.datetime.now())
    utc = dt.datetime.utcnow()
    print("UTC : ", utc)
    print("JD : ", datetime_to_jd(utc))
    print("MJD : ", jd_to_mjd(datetime_to_jd(utc)))
    print("mjdnow(): ", mjdnow())
