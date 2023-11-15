def current_time(tzinfo=None):
    if tzinfo is not None:
        dt = datetime.datetime.now(tzinfo)
    else:
        dt = datetime.datetime.now(dateutil.tz.tzlocal())
    return dt