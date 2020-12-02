import os
import re
import sys
import warnings
from datetime import timezone
from pathlib import Path

from tzlocal import utils

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
else:
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_cache_tz = None


def _tz_from_env(tzenv):
    if tzenv[0] == ':':
        tzenv = tzenv[1:]

    # TZ specifies a file
    tzenv_path = Path(tzenv)
    if tzenv_path.is_absolute() and tzenv_path.exists():
        with tzenv_path.open('rb') as tzfile:
            return ZoneInfo.from_file(tzfile, key='local')

    # TZ specifies a zoneinfo zone.
    try:
        tz = ZoneInfo(tzenv)
        # That worked, so we return this:
        return tz
    except ZoneInfoNotFoundError:
        raise ZoneInfoNotFoundError(
            "tzlocal() does not support non-zoneinfo timezones like %s. \n"
            "Please use a timezone in the form of Continent/City") from None


def _try_tz_from_env():
    tzenv = os.environ.get('TZ')
    if tzenv:
        try:
            return _tz_from_env(tzenv)
        except ZoneInfoNotFoundError:
            pass


def _get_localzone(_root='/'):
    """Tries to find the local timezone configuration.

    This method prefers finding the timezone name and passing that to pytz,
    over passing in the localtime file, as in the later case the zoneinfo
    name is unknown.

    The parameter _root makes the function look for files like /etc/localtime
    beneath the _root directory. This is primarily used by the tests.
    In normal usage you call the function without parameters."""

    tzenv = _try_tz_from_env()
    if tzenv:
        return tzenv

    if not isinstance(_root, os.PathLike):
        _root = Path(_root)

    # Are we under Termux on Android?
    if Path('/system/bin/getprop').exists():
        import subprocess
        androidtz = subprocess.check_output(['getprop', 'persist.sys.timezone']).strip().decode()
        return ZoneInfo(androidtz)

    # Now look for distribution specific configuration files
    # that contain the timezone name.
    for configfile in ('etc/timezone', 'var/db/zoneinfo'):
        tzpath = _root / configfile
        try:
            data = tzpath.read_bytes()
            # Issue #3 was that /etc/timezone was a zoneinfo file.
            # That's a misconfiguration, but we need to handle it gracefully:
            if data[:5] == b'TZif2':
                continue

            etctz = data.strip().decode()
            if not etctz:
                # Empty file, skip
                continue
            for etctz in data.decode().splitlines():
                # Get rid of host definitions and comments:
                if ' ' in etctz:
                    etctz, dummy = etctz.split(' ', 1)
                if '#' in etctz:
                    etctz, dummy = etctz.split('#', 1)
                if not etctz:
                    continue
                tz = ZoneInfo(etctz.replace(' ', '_'))
                if _root == Path('/'):
                    # We are using a file in etc to name the timezone.
                    # Verify that the timezone specified there is actually used:
                    utils.assert_tz_offset(tz)
                return tz

        except IOError:
            # File doesn't exist or is a directory
            continue

    # CentOS has a ZONE setting in /etc/sysconfig/clock,
    # OpenSUSE has a TIMEZONE setting in /etc/sysconfig/clock and
    # Gentoo has a TIMEZONE setting in /etc/conf.d/clock
    # We look through these files for a timezone:

    zone_re = re.compile(r'\s*ZONE\s*=\s*\"')
    timezone_re = re.compile(r'\s*TIMEZONE\s*=\s*\"')
    end_re = re.compile('\"')

    for filename in ('etc/sysconfig/clock', 'etc/conf.d/clock'):
        tzpath = _root / filename
        try:
            for line in tzpath.read_text().splitlines():
                # Look for the ZONE= setting.
                match = zone_re.match(line)
                if match is None:
                    # No ZONE= setting. Look for the TIMEZONE= setting.
                    match = timezone_re.match(line)
                if match is not None:
                    # Some setting existed
                    line = line[match.end():]
                    etctz = line[:end_re.search(line).start()]

                    # We found a timezone
                    tz = ZoneInfo(etctz.replace(' ', '_'))
                    if _root == Path('/'):
                        # We are using a file in etc to name the timezone.
                        # Verify that the timezone specified there is actually used:
                        utils.assert_tz_offset(tz)
                    return tz

        except IOError:
            # File doesn't exist or is a directory
            continue

    # systemd distributions use symlinks that include the zone name,
    # see manpage of localtime(5) and timedatectl(1)
    tzpath = _root / 'etc/localtime'
    if tzpath.exists() and tzpath.is_symlink():
        parts = tzpath.resolve().parts
        for start in range(1, len(parts)):
            try:
                return ZoneInfo('/'.join(parts[start:]))
            except ZoneInfoNotFoundError:
                pass

    # No explicit setting existed. Use localtime
    for filename in ('etc/localtime', 'usr/local/etc/localtime'):
        tzpath = _root / filename
        if tzpath.exists():
            with tzpath.open('rb') as tzfile:
                return ZoneInfo.from_file(tzfile, key='local')

    warnings.warn('Can not find any timezone configuration, defaulting to UTC.')
    return timezone.utc

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
