import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

import tzlocal.unix
import tzlocal.utils

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
else:
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import logging

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope="session", autouse=True)
def clear_tz_env_variable():
    os.environ.pop("TZ", None)


def tz_path(zonefile: str = None) -> str:
    path = Path(__file__).parent.joinpath("test_data")
    if zonefile:
        return str(path / zonefile)
    else:
        return str(path)


def test_env(monkeypatch):
    tz_harare = tzlocal.utils._tz_from_env(":Africa/Harare")
    assert str(tz_harare) == "Africa/Harare"

    # Some Unices allow this as well, so we must allow it:
    tz_harare = tzlocal.utils._tz_from_env("Africa/Harare")
    assert str(tz_harare) == "Africa/Harare"

    path = tz_path(os.path.join("Africa", "Harare"))
    tz_local = tzlocal.utils._tz_from_env(":" + path)
    assert str(tz_local) == "Africa/Harare"
    # Make sure the local timezone is the same as the Harare one above.
    # We test this with a past date, so that we don't run into future changes
    # of the Harare timezone.
    dt = datetime(2012, 1, 1, 5)
    assert dt.replace(tzinfo=tz_harare) == dt.replace(tzinfo=tz_local)

    tz_local = tzlocal.utils._tz_from_env(tz_path("UTC"))
    assert str(tz_local) == "UTC"

    path = tz_path(os.path.join("localtime", "etc", "localtime"))
    tz_local = tzlocal.utils._tz_from_env(path)
    assert str(tz_local) == "localtime"

    # Non-zoneinfo timezones are not supported in the TZ environment.
    pytest.raises(ZoneInfoNotFoundError, tzlocal.utils._tz_from_env, "GMT+03:00")

    # With a zone that doesn't exist, raises error
    pytest.raises(ZoneInfoNotFoundError, tzlocal.utils._tz_from_env, "Just Nonsense")


def test_timezone():
    # Most versions of Ubuntu

    tz = tzlocal.unix._get_localzone(_root=tz_path("timezone"))
    assert str(tz) == "Africa/Harare"


def test_timezone_top_line_comment():
    tz = tzlocal.unix._get_localzone(_root=tz_path("top_line_comment"))
    assert str(tz) == "Africa/Harare"


def test_zone_setting():
    # A ZONE setting in /etc/sysconfig/clock, f ex CentOS

    tz = tzlocal.unix._get_localzone(_root=tz_path("zone_setting"))
    assert str(tz) == "Africa/Harare"


def test_timezone_setting():
    # A ZONE setting in /etc/conf.d/clock, f ex Gentoo

    tz = tzlocal.unix._get_localzone(_root=tz_path("timezone_setting"))
    assert str(tz) == "Africa/Harare"


@pytest.mark.skipif(
    platform.system() == "Windows", reason="Symbolic links are not available on Windows"
)
def test_symlink_localtime():
    # A ZONE setting in the target path of a symbolic linked localtime, f ex systemd distributions

    tz = tzlocal.unix._get_localzone(_root=tz_path("symlink_localtime"))
    assert str(tz) == "Africa/Harare"


def test_vardbzoneinfo_setting():
    # A ZONE setting in /etc/conf.d/clock, f ex Gentoo

    tz = tzlocal.unix._get_localzone(_root=tz_path("vardbzoneinfo"))
    assert str(tz) == "Africa/Harare"


def test_only_localtime():
    tz = tzlocal.unix._get_localzone(_root=tz_path("localtime"))
    assert str(tz) == "local"
    dt = datetime(2012, 1, 1, 5)
    assert dt.replace(tzinfo=ZoneInfo("Africa/Harare")) == dt.replace(tzinfo=tz)


def test_get_reload(mocker, monkeypatch):
    mocker.patch("tzlocal.utils.assert_tz_offset")
    # Clear any cached zone
    monkeypatch.setattr(tzlocal.unix, "_cache_tz", None)
    monkeypatch.setenv("TZ", "Africa/Harare")

    tz_harare = tzlocal.unix.get_localzone()
    assert str(tz_harare) == "Africa/Harare"
    # Changing the TZ makes no difference, because it's cached
    monkeypatch.setenv("TZ", "Africa/Johannesburg")
    tz_harare = tzlocal.unix.get_localzone()
    assert str(tz_harare) == "Africa/Harare"
    # So we reload it
    tz_harare = tzlocal.unix.reload_localzone()
    assert str(tz_harare) == "Africa/Johannesburg"


def test_fail(recwarn):
    with pytest.warns(UserWarning, match="Can not find any timezone configuration"):
        tz = tzlocal.unix._get_localzone(_root=tz_path())
    assert tz == timezone.utc


def test_assert_tz_offset():
    # The local zone should be the local zone:
    local = tzlocal.get_localzone()
    tzlocal.utils.assert_tz_offset(local)

    # Get a non local zone. Let's use Chatham, population 600.
    other = ZoneInfo("Pacific/Chatham")
    pytest.raises(ValueError, tzlocal.utils.assert_tz_offset, other)

    # But you can change it do it only warns
    other = ZoneInfo("Pacific/Chatham")
    with pytest.warns(UserWarning):
        tzlocal.utils.assert_tz_offset(other, error=False)


def test_win32(mocker):
    if sys.platform == "win32":
        # Ironically, these tests don't work on Windows.
        import tzlocal.win32

        # Just check on Windows that the code works, and that we get
        # something reasonable back.
        tz = tzlocal.win32.get_localzone()
        # It should be a timezone with a slash in it, at least:
        assert "/" in str(tz)
        return

    # Yes, winreg is all mocked out, but this test means we at least
    # catch syntax errors, etc.
    mocker.patch("tzlocal.utils.assert_tz_offset")
    winreg = MagicMock()
    winreg.EnumValue.configure_mock(
        return_value=("TimeZoneKeyName", "Belarus Standard Time")
    )
    sys.modules["winreg"] = winreg

    import tzlocal.win32

    tz = tzlocal.win32.get_localzone()
    assert str(tz) == "Europe/Minsk"

    tz = tzlocal.win32.reload_localzone()
    assert str(tz) == "Europe/Minsk"

    winreg.EnumValue.configure_mock(
        return_value=("TimeZoneKeyName", "Not a real timezone")
    )
    pytest.raises(ZoneInfoNotFoundError, tzlocal.win32._get_localzone_name)

    # Old XP style reginfo should fail
    winreg.EnumValue.configure_mock(
        return_value=("TimeZoneKeyName", "Belarus Standard Time")
    )
    tzlocal.win32.valuestodict = Mock(
        return_value={
            "StandardName": "Mocked Standard Time",
            "Std": "Mocked Standard Time",
        }
    )
    pytest.raises(LookupError, tzlocal.win32._get_localzone_name)


def test_win32_env(mocker, monkeypatch):
    sys.modules["winreg"] = MagicMock()
    import tzlocal.win32

    mocker.patch("tzlocal.utils.assert_tz_offset")
    monkeypatch.setattr(tzlocal.win32, "_cache_tz", None)
    monkeypatch.setenv("TZ", "Europe/Berlin")

    tzlocal.win32._cache_tz_name = None
    tzname = tzlocal.win32.get_localzone_name()
    assert tzname == "Europe/Berlin"
    tz = tzlocal.win32.get_localzone()
    assert str(tz) == "Europe/Berlin"


def test_win32_no_dst(mocker):
    mocker.patch("tzlocal.utils.assert_tz_offset")
    valuesmock = mocker.patch("tzlocal.win32.valuestodict")

    # If you turn off the DST, tzlocal returns "Etc/GMT+zomething":
    valuesmock.configure_mock(
        return_value={
            "TimeZoneKeyName": "Romance Standard Time",
            "DynamicDaylightTimeDisabled": 1,
        }
    )
    tzlocal.win32._cache_tz_name = None
    tzlocal.win32._cache_tz = None
    assert str(tzlocal.win32.get_localzone()) == "Etc/GMT-1"

    # Except if the timezone doesn't have daylight savings at all,
    # then just return the timezone in question, because why not?
    valuesmock.configure_mock(
        return_value={
            "TimeZoneKeyName": "Belarus Standard Time",
            "DynamicDaylightTimeDisabled": 1,
        }
    )
    tz = tzlocal.win32._get_localzone_name()
    assert tz == "Europe/Minsk"

    # Now, if you disable this in a timezone with DST, that has a
    # non-whole hour offset, then there's nothing we can return.
    valuesmock.configure_mock(
        return_value={
            "TimeZoneKeyName": "Cen. Australia Standard Time",
            "DynamicDaylightTimeDisabled": 1,
        }
    )
    pytest.raises(ZoneInfoNotFoundError, tzlocal.win32._get_localzone_name)

    # But again, if there is no DST, that works fine:
    valuesmock.configure_mock(
        return_value={
            "TimeZoneKeyName": "Aus Central W. Standard Time",
            "DynamicDaylightTimeDisabled": 1,
        }
    )
    tz = tzlocal.win32._get_localzone_name()
    assert tz == "Australia/Eucla"


def test_termux(mocker):
    subprocess = MagicMock()
    subprocess.check_output.configure_mock(return_value=b"Africa/Johannesburg")
    sys.modules["subprocess"] = subprocess

    tz = tzlocal.unix._get_localzone(_root=tz_path("termux"))
    assert str(tz) == "Africa/Johannesburg"


@pytest.mark.skipif(
    platform.system() == "Windows", reason="Symbolic links are not available on Windows"
)
def test_conflicting():
    with pytest.raises(ZoneInfoNotFoundError) as excinfo:
        tzlocal.unix._get_localzone(_root=tz_path("conflicting"))
    message = excinfo.value.args[0]
    assert "Multiple conflicting time zone configurations found:\n" in message
    assert "Europe/Paris" in message
    assert "America/New_York" in message
    assert "Europe/Warsaw" in message
    assert "Africa/Johannesburg" in message
    assert "localtime is a symlink to: Africa/Harare" in message


@pytest.mark.skipif(
    platform.system() == "Windows", reason="Symbolic links are not available on Windows"
)
def test_noconflict():
    tz = tzlocal.unix._get_localzone(_root=tz_path("noconflict"))
    assert str(tz) == "Etc/UTC"


def test_zoneinfo_compatibility():
    os.environ["TZ"] = "Africa/Harare"
    tzlocal.unix.reload_localzone()
    tz_harare = tzlocal.unix.get_localzone()
    assert str(tz_harare) == "Africa/Harare"

    os.environ["TZ"] = "America/New_York"
    tzlocal.unix.reload_localzone()
    tz_newyork = tzlocal.unix.get_localzone()
    assert str(tz_newyork) == "America/New_York"

    dt = datetime(2021, 10, 1, 12, 00)
    dt = dt.replace(tzinfo=tz_harare)
    assert dt.utcoffset().total_seconds() == 7200
    dt = dt.replace(tzinfo=tz_newyork)
    assert dt.utcoffset().total_seconds() == -14400
    del os.environ["TZ"]


def test_get_localzone_name():
    tzlocal.unix._cache_tz_name = None
    os.environ["TZ"] = "America/New_York"
    assert tzlocal.unix.get_localzone_name() == "America/New_York"
    del os.environ["TZ"]


def test_ubuntu_docker_bug():
    tz = tzlocal.unix._get_localzone(_root=tz_path("ubuntu_docker_bug"))
    assert str(tz) == "UTC"
