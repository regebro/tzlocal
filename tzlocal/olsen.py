from tzlocal.windows_tz import tz_names_olsen

def get_windowszone_name(tz):
    """Get the TimeZone Name as the Windows TimeZone Name"""
    if tz is None:
        raise pytz.UnknownTimeZoneError('Can not find any timezone configuration')

    else:
        tzkeyname = tz.zone
        timezone = tz_names_olsen.get(tzkeyname)

        if timezone is None:
            timezone = "Unknown"

        return timezone

def get_olsenzone_name(tz):
    """Get the TimeZone Name as the Olzen TimeZone Name"""
    if tz is None:
        raise pytz.UnknownTimeZoneError('Can not find any timezone configuration')
    else:
        return tz.zone
