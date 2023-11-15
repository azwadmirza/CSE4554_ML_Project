def to_nice_json(*a, **kw):
    '''Make verbose, human readable JSON'''
    return json.dumps(*a, indent=4, sort_keys=True, **kw)