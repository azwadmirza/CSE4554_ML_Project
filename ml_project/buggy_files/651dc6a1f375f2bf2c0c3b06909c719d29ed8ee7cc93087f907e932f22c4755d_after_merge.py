def get_date(schedule=False, rule=None, last_date=None, tz=None, iso8601=False):
    """Returns a date stamp, given a recurrence rule.

    schedule - bool:
        whether to use the recurrence rule or not

    rule - str:
        an iCal RRULE string that specifies the rule for scheduling posts

    last_date - datetime:
        timestamp of the last post

    tz - tzinfo:
        the timezone used for getting the current time.

    iso8601 - bool:
        whether to force ISO 8601 dates (instead of locale-specific ones)

    """

    if tz is None:
        tz = dateutil.tz.tzlocal()
    date = now = datetime.datetime.now(tz)
    if schedule:
        try:
            from dateutil import rrule
        except ImportError:
            LOGGER.error('To use the --schedule switch of new_post, '
                         'you have to install the "dateutil" package.')
            rrule = None  # NOQA
    if schedule and rrule and rule:
        try:
            rule_ = rrule.rrulestr(rule, dtstart=last_date)
        except Exception:
            LOGGER.error('Unable to parse rule string, using current time.')
        else:
            date = rule_.after(max(now, last_date or now), last_date is None)

    offset = tz.utcoffset(now)
    offset_sec = (offset.days * 24 * 3600 + offset.seconds)
    offset_hrs = offset_sec // 3600
    offset_min = offset_sec % 3600
    if iso8601:
        tz_str = '{0:+03d}:{1:02d}'.format(offset_hrs, offset_min // 60)
    else:
        if offset:
            tz_str = ' UTC{0:+03d}:{1:02d}'.format(offset_hrs, offset_min // 60)
        else:
            tz_str = ' UTC'

    return date.strftime('%Y-%m-%d %H:%M:%S') + tz_str