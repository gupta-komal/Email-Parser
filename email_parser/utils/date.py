import datetime

from email.utils import parsedate_tz

__all__ = [
    'convert_date_str_to_date',
]


class TZInfo(datetime.tzinfo):
    def __init__(self, offset):
        """
        :param offset: UTC offset in seconds.
        :type offset: ``int``
        """
        self.offset = offset

    def utcoffset(self, dt):
        return datetime.timedelta(seconds=self.offset)

    def tzname(self, dt):
        return ''

    def dst(self, dt):
        return datetime.timedelta(0)


def convert_date_str_to_date(date_str):
    """
    Convert date string to a time-zone aware datetime object.

    :param date_str: Date in the following format:
                    "Wed, 9 Oct 2013 00:39:59 +0200"
    :type date_str: ``str``

    :rtype: ``datetime.datetime``
    """
    parsed = parsedate_tz(date_str)
    date = datetime.datetime(*parsed[0:6])
    offset = parsed[-1]
    tzinfo = TZInfo(offset)
    date = date.replace(tzinfo=tzinfo)
    return date
