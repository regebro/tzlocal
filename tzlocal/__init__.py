import sys
if sys.platform == 'win32':
    from tzlocal.win32 import get_localzone, reload_localzone
else:
    from tzlocal.unix import get_localzone, reload_localzone

from .pytzshim import add_key_attribute
add_key_attribute()

__all__ = ['get_localzone', 'reload_localzone']


