from __future__ import with_statement
import Foundation
from datetime import tzinfo, timedelta

_cache_tz = None


class TZ(tzinfo):

    def __init__(self):
        tz = Foundation.NSTimeZone.systemTimeZone()

        self._utcoffset = timedelta(seconds=tz.secondsFromGMT())
        self._tzname = tz.name()

        if tz.isDaylightSavingTime():
            self._dst = timedelta(seconds=3600)
        else:
            self._dst = timedelta()

    def utcoffset(self, dt):
        return self._utcoffset

    def tzname(self, dt):
        return self._tzname

    def dst(self, dt):
        return self._dst


def get_localzone():
    """Get the computers configured local timezone, if any."""
    global _cache_tz
    if _cache_tz is None:
        _cache_tz = TZ()
    return _cache_tz


def reload_localzone():
    """Reload the cached localzone. You need to call this if the timezone has changed."""
    global _cache_tz
    _cache_tz = TZ()
    return _cache_tz
