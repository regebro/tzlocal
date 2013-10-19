from __future__ import with_statement
import os
import re
import pytz

_cache_tz = None

def _get_localzone():
    tzname = os.popen("systemsetup -gettimezone").read().replace("Time Zone: ", "").strip()
    return pytz.timezone(tzname)

def get_localzone():
    """Get the computers configured local timezone, if any."""
    global _cache_tz
    if _cache_tz is None:
        _cache_tz = _get_localzone()
    return _cache_tz

def reload_localzone():
    """Reload the cached localzone. You need to call this if the timezone has changed."""
    global _cache_tz
    _cache_tz = _get_localzone()
    return _cache_tz
    