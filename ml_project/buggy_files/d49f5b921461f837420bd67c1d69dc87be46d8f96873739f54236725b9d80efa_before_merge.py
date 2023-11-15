def timesince_last_update(last_update, time_prefix='', use_shorthand=True):
    """
    Returns:
         - the time of update if last_update is today, if any prefix is supplied, the output will use it
         - time since last update othewise. Defaults to the simplified timesince,
           but can return the full string if needed
    """
    if last_update.date() == datetime.today().date():
        time_str = timezone.localtime(last_update).strftime("%H:%M")
        return time_str if not time_prefix else '%(prefix)s %(formatted_time)s' % {
            'prefix': time_prefix, 'formatted_time': time_str
        }
    else:
        if use_shorthand:
            return timesince_simple(last_update)
        return _("%(time_period)s ago") % {'time_period': timesince(last_update)}