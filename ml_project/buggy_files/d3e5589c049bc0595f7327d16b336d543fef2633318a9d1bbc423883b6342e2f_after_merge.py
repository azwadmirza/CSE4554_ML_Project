def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime)):
        return obj.isoformat()
    if isinstance(obj, (timedelta)):
        return {
            '__type__': 'timedelta',
            'days': obj.days,
            'seconds': obj.seconds,
            'microseconds': obj.microseconds,
        }
    raise TypeError ("Type %s not serializable" % type(obj))