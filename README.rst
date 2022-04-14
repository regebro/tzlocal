tzlocal
=======

API CHANGE!
-----------

With version 3.0 of tzlocal, tzlocal no longer returned `pytz` objects, but
`zoneinfo` objects, which has a different API. Since 4.0, it now restored
partial compatibility for `pytz` users through Paul Ganssle's
`pytz_deprecation_shim`.

tzlocal 4.0 also adds an official function `get_localzone_name()` to get only
the timezone name, instead of a timezone object. On unix, it can raise an
error if you don't have a timezone name configured, where `get_localzone()`
will succeed, so only use that if you need the timezone name.

4.0 also adds way more information on what is going wrong in your
configuration when the configuration files are unclear or contradictory.


Info
----

This Python module returns a ``tzinfo`` object (with a pytz_deprecation_shim,
for pytz compatibility) with the local timezone information, under Unix and
Windows.

It requires Python 3.6 or later, and will use the ``backports.tzinfo``
package, for Python 3.6 to 3.8.

This module attempts to fix a glaring hole in the ``pytz`` and ``zoneinfo``
modules, that there is no way to get the local timezone information, unless
you know the zoneinfo name, and under several Linux distros that's hard or
impossible to figure out.

With ``tzlocal`` you only need to call ``get_localzone()`` and you will get a
``tzinfo`` object with the local time zone info. On some Unices you will
still not get to know what the timezone name is, but you don't need that when
you have the tzinfo file. However, if the timezone name is readily available
it will be used.


Supported systems
-----------------

These are the systems that are in theory supported:

 * Windows 2000 and later

 * Any unix-like system with a ``/etc/localtime`` or ``/usr/local/etc/localtime``

If you have one of the above systems and it does not work, it's a bug.
Please report it.

Please note that if you are getting a time zone called ``local``, this is not
a bug, it's actually the main feature of ``tzlocal``, that even if your
system does NOT have a configuration file with the zoneinfo name of your time
zone, it will still work.

You can also use ``tzlocal`` to get the name of your local timezone, but only
if your system is configured to make that possible. ``tzlocal`` looks for the
timezone name in ``/etc/timezone``, ``/var/db/zoneinfo``,
``/etc/sysconfig/clock`` and ``/etc/conf.d/clock``. If your
``/etc/localtime`` is a symlink it can also extract the name from that
symlink.

If you need the name of your local time zone, then please make sure your
system is properly configured to allow that.

If your unix system doesn't have a timezone configured, tzlocal will default
to UTC.

Notes on Docker
---------------

It turns out that Docker images frequently have broken timezone setups.
This usually resuts in a warning that the configuration is wrong, or that
the timezone offset doesn't match the found timezone.

The easiest way to fix that is to set a TZ variable in your docker setup
to whatever timezone you want, which is usually the timezone your host
computer has.

Usage
-----

Load the local timezone:

    >>> from tzlocal import get_localzone
    >>> tz = get_localzone()
    >>> tz
    <DstTzInfo 'Europe/Warsaw' WMT+1:24:00 STD>

Create a local datetime:

    >>> from datetime import datetime
    >>> dt = datetime(2015, 4, 10, 7, 22, tzinfo=tz)
    >>> dt
    datetime.datetime(2015, 4, 10, 7, 22, tzinfo=<DstTzInfo 'Europe/Warsaw' CEST+2:00:00 DST>)

Lookup another timezone with ``zoneinfo`` (``backports.zoneinfo`` on Python 3.8 or earlier):

    >>> from zoneinfo import ZoneInfo
    >>> eastern = ZoneInfo('US/Eastern')

Convert the datetime:

    >>> dt.astimezone(eastern)
    datetime.datetime(2015, 4, 10, 1, 22, tzinfo=<DstTzInfo 'US/Eastern' EDT-1 day, 20:00:00 DST>)

If you just want the name of the local timezone, use `get_localzone_name()`:

    >>> from tzlocal import get_localzone_name
    >>> get_localzone_name()
    "Europe/Warsaw"

Please note that under Unix, `get_localzone_name()` may fail if there is no zone
configured, where `get_localzone()` would generally succeed.


Development
-----------

To create a development environment, create a virtualenv and make a development installation::

    $ virtualenv ve
    $ source ve/bin/activation (Win32: .\ve\Scripts\activate)
    (ve) $ pip install -e .[test,devenv]

To run tests, just use pytest, coverage is nice as well::

    (ve) $ pytest --cov=tzlocal



Maintainer
----------

* Lennart Regebro, regebro@gmail.com

Contributors
------------

* Marc Van Olmen
* Benjamen Meyer
* Manuel Ebert
* Xiaokun Zhu
* Cameris
* Edward Betts
* McK KIM
* Cris Ewing
* Ayala Shachar
* Lev Maximov
* Jakub Wilk
* John Quarles
* Preston Landers
* Victor Torres
* Jean Jordaan
* Zackary Welch
* Mickaël Schoentgen
* Gabriel Corona
* Alex Grönholm
* Julin S
* Miroslav Šedivý
* revansSZ
* Sam Treweek

(Sorry if I forgot someone)

License
-------

* MIT https://opensource.org/licenses/MIT
