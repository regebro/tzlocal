import os
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


@pytest.fixture(scope='session', autouse=True)
def clear_tz_env_variable():
    os.environ.pop('TZ', None)


@pytest.fixture
def tz_path(request):
    path = Path(__file__).parent.joinpath('test_data')
    if hasattr(request, 'param'):
        return str(path / request.param)
    else:
        return str(path)


@pytest.mark.parametrize('tz_path', ['Harare'], indirect=True)
def test_env(tz_path, monkeypatch):
    tz_harare = tzlocal.unix._tz_from_env(':Africa/Harare')
    assert tz_harare.key == 'Africa/Harare'

    # Some Unices allow this as well, so we must allow it:
    tz_harare = tzlocal.unix._tz_from_env('Africa/Harare')
    assert tz_harare.key == 'Africa/Harare'

    tz_local = tzlocal.unix._tz_from_env(':' + tz_path)
    assert tz_local.key == 'local'
    # Make sure the local timezone is the same as the Harare one above.
    # We test this with a past date, so that we don't run into future changes
    # of the Harare timezone.
    dt = datetime(2012, 1, 1, 5)
    assert dt.replace(tzinfo=tz_harare) == dt.replace(tzinfo=tz_local)

    # Non-zoneinfo timezones are not supported in the TZ environment.
    pytest.raises(ZoneInfoNotFoundError, tzlocal.unix._tz_from_env, 'GMT+03:00')

    # Test the _try function
    monkeypatch.setenv('TZ', 'Africa/Harare')
    tz_harare = tzlocal.unix._try_tz_from_env()
    assert tz_harare.key == 'Africa/Harare'

    # With a zone that doesn't exist
    monkeypatch.setenv('TZ', 'Just Nonsense')
    tz_harare = tzlocal.unix._try_tz_from_env()
    assert tz_harare is None


@pytest.mark.parametrize('tz_path', ['timezone'], indirect=True)
def test_timezone(tz_path):
    # Most versions of Ubuntu

    tz = tzlocal.unix._get_localzone(_root=tz_path)
    assert tz.key == 'Africa/Harare'


@pytest.mark.parametrize('tz_path', ['top_line_comment'], indirect=True)
def test_timezone_top_line_comment(tz_path):
    tz = tzlocal.unix._get_localzone(_root=tz_path)
    assert tz.key == 'Africa/Harare'


@pytest.mark.parametrize('tz_path', ['zone_setting'], indirect=True)
def test_zone_setting(tz_path):
    # A ZONE setting in /etc/sysconfig/clock, f ex CentOS

    tz = tzlocal.unix._get_localzone(_root=tz_path)
    assert tz.key == 'Africa/Harare'


@pytest.mark.parametrize('tz_path', ['timezone_setting'], indirect=True)
def test_timezone_setting(tz_path):
    # A ZONE setting in /etc/conf.d/clock, f ex Gentoo

    tz = tzlocal.unix._get_localzone(_root=tz_path)
    assert tz.key == 'Africa/Harare'


@pytest.mark.parametrize('tz_path', ['symlink_localtime'], indirect=True)
def test_symlink_localtime(tz_path):
    # A ZONE setting in the target path of a symbolic linked localtime, f ex systemd distributions

    tz = tzlocal.unix._get_localzone(_root=tz_path)
    assert tz.key == 'Africa/Harare'


@pytest.mark.parametrize('tz_path', ['vardbzoneinfo'], indirect=True)
def test_vardbzoneinfo_setting(tz_path):
    # A ZONE setting in /etc/conf.d/clock, f ex Gentoo

    tz = tzlocal.unix._get_localzone(_root=tz_path)
    assert tz.key == 'Africa/Harare'


@pytest.mark.parametrize('tz_path', ['localtime'], indirect=True)
def test_only_localtime(tz_path):
    tz = tzlocal.unix._get_localzone(_root=tz_path)
    assert tz.key == 'local'
    dt = datetime(2012, 1, 1, 5)
    assert dt.replace(tzinfo=ZoneInfo('Africa/Harare')) == dt.replace(tzinfo=tz)


def test_get_reload(mocker, monkeypatch):
    mocker.patch('tzlocal.utils.assert_tz_offset')
    # Clear any cached zone
    monkeypatch.setattr(tzlocal.unix, '_cache_tz', None)
    monkeypatch.setenv('TZ', 'Africa/Harare')
    tz_harare = tzlocal.unix.get_localzone()
    assert tz_harare.key == 'Africa/Harare'
    # Changing the TZ makes no difference, because it's cached
    monkeypatch.setenv('TZ', 'Africa/Johannesburg')
    tz_harare = tzlocal.unix.get_localzone()
    assert tz_harare.key == 'Africa/Harare'
    # So we reload it
    tz_harare = tzlocal.unix.reload_localzone()
    assert tz_harare.key == 'Africa/Johannesburg'


def test_fail(tz_path, recwarn):
    with pytest.warns(UserWarning, match='Can not find any timezone configuration'):
        tz = tzlocal.unix._get_localzone(_root=tz_path)
    assert tz == timezone.utc


def test_assert_tz_offset():
    # The local zone should be the local zone:
    local = tzlocal.get_localzone()
    tzlocal.utils.assert_tz_offset(local)

    # Get a non local zone. Let's use Chatham, population 600.
    other = ZoneInfo('Pacific/Chatham')
    pytest.raises(ValueError, tzlocal.utils.assert_tz_offset, other)


def test_win32(mocker):
    if sys.platform == 'win32':
        import tzlocal.win32
        tzlocal.win32.get_localzone()
        return

    # Yes, winreg is all mocked out, but this test means we at least
    # catch syntax errors, etc.
    mocker.patch('tzlocal.utils.assert_tz_offset')
    winreg = MagicMock()
    winreg.EnumValue.configure_mock(return_value=('TimeZoneKeyName','Belarus Standard Time'))
    winreg.EnumKey.configure_mock(return_value='Bahia Standard Time')
    sys.modules['winreg'] = winreg
    import tzlocal.win32
    tz = tzlocal.win32.get_localzone()
    assert tz.key == 'Europe/Minsk'

    tzlocal.win32.valuestodict = Mock(return_value={
        'StandardName': 'Mocked Standard Time',
        'Std': 'Mocked Standard Time',
    })
    tz = tzlocal.win32.reload_localzone()
    assert tz.key == 'America/Bahia'
