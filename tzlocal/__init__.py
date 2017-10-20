import sys

__version__ = "1.5dev0"

# Cache variable
_cache_tz = None

def get_localzone():
    """Returns the zoneinfo-based tzinfo object that matches the local system's timezone."""
    global _cache_tz

    if _cache_tz is not None:
        return _cache_tz

    # Avoid importing sub-modules at load time, breaks running setup.py
    if sys.platform == 'win32':
        from tzlocal.win32 import _get_localzone
    elif 'darwin' in sys.platform:
        from tzlocal.darwin import _get_localzone
    else:
        from tzlocal.unix import _get_localzone

    if _cache_tz == 'local':
        import pytz
        raise pytz.UnknownTimeZoneError("Got timezone 'local', this is not a valid local timezone code")

    return _cache_tz


def reload_localzone():
    """Reload the cached local timezone. You need to call this if the timezone has changed."""
    global _cache_tz
    _cache_tz = get_localzone()
    return _cache_tz
