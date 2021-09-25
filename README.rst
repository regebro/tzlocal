tzlocal
=======

API CHANGE!
-----------

With version 3.0 of tzlocal, it no longer returns `pytz` objects, but `zoneinfo` objects.
This, and the dropping of Python 2 support, are the only differences, so if you need to
use `pytz` objects, you can continue to use tzlocal 2.1.

If there is demand for it, I may continue to support the 2 branch for some time.

Also, the upcoming 4.0 version will add an official function to get the timezone name,
instead of a timezone object, and getting the timezone object will be deprecated, as
Python3.9's `zoneinfo` library supports `ZoneInfo('localtime')`, which is what tzlocal
returns if it can't find a timezone name. Therefore, tzlocal is now only useful to
get the timezone name.

In hindsight, that SHOULD have been the API change for 3.0. Sorry about that.


Info
----

This Python module returns a ``tzinfo`` object with the local timezone information
under Unix and Windows.
It requires either Python 3.9+ or the ``backports.tzinfo`` package, and returns
``zoneinfo.ZoneInfo`` objects.

This module attempts to fix a glaring hole in the ``zoneinfo`` module, that
there is no way to get the local timezone information, unless you know the
zoneinfo name, and under several Linux distros that's hard or impossible to figure out.

With ``tzlocal`` you only need to call ``get_localzone()`` and you will get a
``tzinfo`` object with the local time zone info. On some Unices you will still
not get to know what the timezone name is, but you don't need that when you
have the tzinfo file. However, if the timezone name is readily available it
will be used.


Supported systems
-----------------

These are the systems that are in theory supported:

 * Windows 2000 and later

 * Any unix-like system with a ``/etc/localtime`` or ``/usr/local/etc/localtime``

If you have one of the above systems and it does not work, it's a bug.
Please report it.

Please note that if you are getting a time zone called ``local``, this is not a bug, it's
actually the main feature of ``tzlocal``, that even if your system does NOT have a configuration file
with the zoneinfo name of your time zone, it will still work.

You can also use ``tzlocal`` to get the name of your local timezone, but only if your system is
configured to make that possible. ``tzlocal`` looks for the timezone name in ``/etc/timezone``, ``/var/db/zoneinfo``,
``/etc/sysconfig/clock`` and ``/etc/conf.d/clock``. If your ``/etc/localtime`` is a symlink it can also extract the
name from that symlink.

If you need the name of your local time zone, then please make sure your system is properly configured to allow that.
If it isn't configured, tzlocal will default to UTC.

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
