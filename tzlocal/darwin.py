from __future__ import with_statement
import os
import pytz
import subprocess
import sys


if sys.version_info[0] == 2:

    class Popen(subprocess.Popen):

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            if self.stdout:
                self.stdout.close()
            if self.stderr:
                self.stderr.close()
            if self.stdin:
                self.stdin.close()
            # Wait for the process to terminate, to avoid zombies.
            self.wait()

else:
    from subprocess import Popen


def get_localzone_name(_root='/'):
    with Popen(
        "systemsetup -gettimezone",
        shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    ) as pipe:
        tzname = pipe.stdout.read().replace(b'Time Zone: ', b'').strip()

    if not tzname or tzname not in pytz.all_timezones_set:
        # link will be something like /usr/share/zoneinfo/America/Los_Angeles.
        link = os.readlink(os.path.join(_root, "etc/localtime"))
        tzname = link[link.rfind("zoneinfo/") + 9:]

    return tzname


def _get_localzone():
    """Returns the zoneinfo-based tzinfo object that matches the Windows-configured timezone."""
    return pytz.timezone(get_localzone_name())
