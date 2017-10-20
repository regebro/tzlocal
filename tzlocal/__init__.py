import sys


_cache_tz = None


__version__ = "1.5dev0"


def get_localzone():
    """Returns the zoneinfo-based tzinfo object that matches the local system's timezone."""
    global _cache_tz
    
    # Avoid importing sub-modules at load time, breaks running setup.py
    if sys.platform == 'win32':
        from tzlocal.win32 import _get_localzone
    elif 'darwin' in sys.platform:
        from tzlocal.darwin import _get_localzone
    else:
        from tzlocal.unix import _get_localzone

    if _cache_tz is None:
        _cache_tz = _get_localzone()
    return _cache_tz


def reload_localzone():
    """Reload the cached local timezone. You need to call this if the timezone has changed."""
    global _cache_tz
    _cache_tz = get_localzone()
    return _cache_tz
