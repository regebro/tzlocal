import pytz_deprecation_shim as pds

try:
    import _winreg as winreg
except ImportError:
    import winreg

from tzlocal.windows_tz import win_tz
from tzlocal import utils

_cache_tz = None
_cache_tz_name = None


def valuestodict(key):
    """Convert a registry key's values to a dictionary."""
    dict = {}
    size = winreg.QueryInfoKey(key)[1]
    for i in range(size):
        data = winreg.EnumValue(key, i)
        dict[data[0]] = data[1]
    return dict


def _get_localzone_name():
    # Windows is special. It has unique time zone names (in several
    # meanings of the word) available, but unfortunately, they can be
    # translated to the language of the operating system, so we need to
    # do a backwards lookup, by going through all time zones and see which
    # one matches.
    tzenv = utils._tz_name_from_env()
    if tzenv:
        return tzenv

    handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

    TZLOCALKEYNAME = r"SYSTEM\CurrentControlSet\Control\TimeZoneInformation"
    localtz = winreg.OpenKey(handle, TZLOCALKEYNAME)
    keyvalues = valuestodict(localtz)
    localtz.Close()

    if "TimeZoneKeyName" in keyvalues:
        # Windows 7 and later

        # For some reason this returns a string with loads of NUL bytes at
        # least on some systems. I don't know if this is a bug somewhere, I
        # just work around it.
        tzkeyname = keyvalues["TimeZoneKeyName"].split("\x00", 1)[0]
    else:
        # Don't support XP any longer
        raise LookupError("Can not find Windows timezone configuration")

    timezone = win_tz.get(tzkeyname)
    if timezone is None:
        # Nope, that didn't work. Try adding "Standard Time",
        # it seems to work a lot of times:
        timezone = win_tz.get(tzkeyname + " Standard Time")

    # Return what we have.
    if timezone is None:
        raise utils.ZoneInfoNotFoundError(tzkeyname)

    return timezone


def get_localzone_name():
    """Get the zoneinfo timezone name that matches the Windows-configured timezone."""
    global _cache_tz_name
    if _cache_tz_name is None:
        _cache_tz_name = _get_localzone_name()

    return _cache_tz_name


def get_localzone():
    """Returns the zoneinfo-based tzinfo object that matches the Windows-configured timezone."""

    global _cache_tz
    if _cache_tz is None:
        _cache_tz = pds.timezone(get_localzone_name())

    if not utils._tz_name_from_env():
        # If the timezone does NOT come from a TZ environment variable,
        # verify that it's correct. If it's from the environment,
        # we accept it, this is so you can run tests with different timezones.
        utils.assert_tz_offset(_cache_tz)

    return _cache_tz


def reload_localzone():
    """Reload the cached localzone. You need to call this if the timezone has changed."""
    global _cache_tz
    global _cache_tz_name
    _cache_tz_name = _get_localzone_name()
    _cache_tz = pds.timezone(_cache_tz_name)
    utils.assert_tz_offset(_cache_tz)
    return _cache_tz
