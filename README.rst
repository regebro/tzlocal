tzlocal
=======

This Python module returns a `tzinfo` object with the local timezone information under Unix and Win-32.
It requires `pytz`, and returns `pytz` `tzinfo` objects.

This module attempts to fix a glaring hole in `pytz`, that there is no way to
get the local timezone information, unless you know the zoneinfo name, and
under several Linux distros that's hard or impossible to figure out.

Also, with Windows different timezone system using pytz isn't of much use
unless you separately configure the zoneinfo timezone name.

With `tzlocal` you only need to call `get_localzone()` and you will get a
`tzinfo` object with the local time zone info. On some Unices you will still
not get to know what the timezone name is, but you don't need that when you
have the tzinfo file. However, if the timezone name is readily available it
will be used.


Usage
-----

Load the local timezone:

    >>> from tzlocal import get_localzone
    >>> tz = get_localzone()
    >>> tz
    <DstTzInfo 'Europe/Warsaw' WMT+1:24:00 STD>
    
Create a local datetime:

    >>> from datetime import datetime
    >>> dt = tz.localize(datetime.now())
    >>> dt
    datetime.datetime(2012, 9, 11, 14, 43, 42, 518871, tzinfo=<DstTzInfo 'Europe/Warsaw' CEST+2:00:00 DST>)
    
Lookup another timezone with `pytz`:

    >>> import pytz
    >>> eastern = pytz.timezone('US/Eastern')
    
Convert the datetime:

    >>> dt.astimezone(eastern)
    datetime.datetime(2012, 9, 11, 8, 43, 42, 518871, tzinfo=<DstTzInfo 'US/Eastern' EDT-1 day, 20:00:00 DST>)


Contributors
------------

* Lennart Regebro, regebro@gmail.com

License
-------

* CC0 1.0 Universal  http://creativecommons.org/publicdomain/zero/1.0/
