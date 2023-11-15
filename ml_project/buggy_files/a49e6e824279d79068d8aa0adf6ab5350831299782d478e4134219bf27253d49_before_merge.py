def current_time(tzinfo=None):
    if tzinfo is not None:
        dt = datetime.datetime.utcnow()
        dt = tzinfo.fromutc(dt)
    else:
        dt = datetime.datetime.now(dateutil.tz.tzlocal())
    return dt