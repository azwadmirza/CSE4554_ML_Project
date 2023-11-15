def format_time_seconds(time):
    from quodlibet import ngettext

    time_str = locale.format("%d", time, grouping=True)
    return ngettext("%s second", "%s seconds", time) % time_str