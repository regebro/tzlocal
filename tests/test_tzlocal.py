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
    assert tz_harare.key == "Africa/Harare"

    # Some Unices allow this as well, so we must allow it:
    tz_harare = tzlocal.utils._tz_from_env("Africa/Harare")
    assert tz_harare.key == "Africa/Harare"

    tz_local = tzlocal.utils._tz_from_env(":" + tz_path("Harare"))
    assert tz_local.key == "Harare"
    # Make sure the local timezone is the same as the Harare one above.
    # We test this with a past date, so that we don't run into future changes
    # of the Harare timezone.
    dt = datetime(2012, 1, 1, 5)
    assert dt.replace(tzinfo=tz_harare) == dt.replace(tzinfo=tz_local)

    # Non-zoneinfo timezones are not supported in the TZ environment.
    pytest.raises(ZoneInfoNotFoundError, tzlocal.utils._tz_from_env, "GMT+03:00")

    # With a zone that doesn't exist, raises error
    monkeypatch.setenv("TZ", "Just Nonsense")
    pytest.raises(ZoneInfoNotFoundError, tzlocal.utils._tz_from_env)


def test_timezone():
    # Most versions of Ubuntu

    tz = tzlocal.unix._get_localzone(_root=tz_path("timezone"))
    assert tz.key == "Africa/Harare"


def test_timezone_top_line_comment():
    tz = tzlocal.unix._get_localzone(_root=tz_path("top_line_comment"))
    assert tz.key == "Africa/Harare"


def test_zone_setting():
    # A ZONE setting in /etc/sysconfig/clock, f ex CentOS

    tz = tzlocal.unix._get_localzone(_root=tz_path("zone_setting"))
    assert tz.key == "Africa/Harare"


def test_timezone_setting():
    # A ZONE setting in /etc/conf.d/clock, f ex Gentoo

    tz = tzlocal.unix._get_localzone(_root=tz_path("timezone_setting"))
    assert tz.key == "Africa/Harare"


@pytest.mark.skipif(
    platform.system() == "Windows", reason="Symbolic links are not available on Windows"
)
def test_symlink_localtime():
    # A ZONE setting in the target path of a symbolic linked localtime, f ex systemd distributions

    tz = tzlocal.unix._get_localzone(_root=tz_path("symlink_localtime"))
    assert tz.key == "Africa/Harare"


def test_vardbzoneinfo_setting():
    # A ZONE setting in /etc/conf.d/clock, f ex Gentoo

    tz = tzlocal.unix._get_localzone(_root=tz_path("vardbzoneinfo"))
    assert tz.key == "Africa/Harare"


def test_only_localtime():
    tz = tzlocal.unix._get_localzone(_root=tz_path("localtime"))
    assert tz.key == "local"
    dt = datetime(2012, 1, 1, 5)
    assert dt.replace(tzinfo=ZoneInfo("Africa/Harare")) == dt.replace(tzinfo=tz)


def test_get_reload(mocker, monkeypatch):
    mocker.patch("tzlocal.utils.assert_tz_offset")
    # Clear any cached zone
    monkeypatch.setattr(tzlocal.unix, "_cache_tz", None)
    monkeypatch.setenv("TZ", "Africa/Harare")

    tz_harare = tzlocal.unix.get_localzone()
    assert tz_harare.key == "Africa/Harare"
    # Changing the TZ makes no difference, because it's cached
    monkeypatch.setenv("TZ", "Africa/Johannesburg")
    tz_harare = tzlocal.unix.get_localzone()
    assert tz_harare.key == "Africa/Harare"
    # So we reload it
    tz_harare = tzlocal.unix.reload_localzone()
    assert tz_harare.key == "Africa/Johannesburg"


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


def test_win32(mocker):
    if sys.platform == "win32":
        import tzlocal.win32

        tzlocal.win32.get_localzone()
        return

    # Yes, winreg is all mocked out, but this test means we at least
    # catch syntax errors, etc.
    mocker.patch("tzlocal.utils.assert_tz_offset")
    winreg = MagicMock()
    winreg.EnumValue.configure_mock(
        return_value=("TimeZoneKeyName", "Belarus Standard Time")
    )
    winreg.EnumKey.configure_mock(return_value="Bahia Standard Time")
    sys.modules["winreg"] = winreg
    import tzlocal.win32

    tz = tzlocal.win32.get_localzone()
    assert tz.key == "Europe/Minsk"

    tzlocal.win32.valuestodict = Mock(
        return_value={
            "StandardName": "Mocked Standard Time",
            "Std": "Mocked Standard Time",
        }
    )
    tz = tzlocal.win32.reload_localzone()
    assert tz.key == "America/Bahia"


def test_termux(mocker):
    subprocess = MagicMock()
    subprocess.check_output.configure_mock(return_value=b"Africa/Johannesburg")
    sys.modules["subprocess"] = subprocess

    tz = tzlocal.unix._get_localzone(_root=tz_path("termux"))
    assert tz.key == "Africa/Johannesburg"


def test_conflicting():
    with pytest.raises(ZoneInfoNotFoundError) as excinfo:
        tz = tzlocal.unix._get_localzone(_root=tz_path("conflicting"))
    message = excinfo.value.args[0]
    assert "Multiple conflicting time zone configurations found:\n" in message
    assert "Europe/Paris" in message
    assert "America/New_York" in message
    assert "Europe/Warsaw" in message
    assert "Africa/Johannesburg" in message


def test_noconflict():
    tz = tzlocal.unix._get_localzone(_root=tz_path("noconflict"))
    assert tz.key == "UTC"

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
    assert tz.key == "Europe/Berlin"
