def get_local_timezone():
    """Returns the Olson identifier of the local timezone.
    In a happy world, tzlocal.get_localzone would do this, but there's a bug on OS X
    that prevents that right now: https://github.com/regebro/tzlocal/issues/6"""
    global __cached_tz
    if not __cached_tz and "darwin" in sys.platform:
        __cached_tz = os.popen("systemsetup -gettimezone").read().replace("Time Zone: ", "").strip()
    if not __cached_tz or __cached_tz not in pytz.all_timezones_set:
        link = os.readlink("/etc/localtime")
        # This is something like /usr/share/zoneinfo/America/Los_Angeles.
        # Find second / from right and take the substring
        __cached_tz = link[link.rfind('/', 0, link.rfind('/'))+1:]
    if not __cached_tz or __cached_tz not in pytz.all_timezones_set:
        __cached_tz = str(get_localzone())
    if not __cached_tz or __cached_tz not in pytz.all_timezones_set:
        __cached_tz = "UTC"
    return __cached_tz