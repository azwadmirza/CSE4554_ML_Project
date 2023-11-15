def format_timestamp(t):
    """Cast given object to a Timestamp and return a nicely formatted string"""
    datetime_str = str(pd.Timestamp(t))
    try:
        date_str, time_str = datetime_str.split()
    except ValueError:
        # catch NaT and others that don't split nicely
        return datetime_str
    else:
        if time_str == '00:00:00':
            return date_str
        else:
            return '%sT%s' % (date_str, time_str)