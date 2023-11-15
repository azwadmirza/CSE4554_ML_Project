def format_time_seconds(time):
    from quodlibet import ngettext

    time_str = format_int_locale(time)
    return ngettext("%s second", "%s seconds", time) % time_str