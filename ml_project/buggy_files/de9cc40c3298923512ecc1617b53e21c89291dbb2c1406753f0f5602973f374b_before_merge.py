def json_dump(object):
    return json.dumps(object, indent=2, sort_keys=True,
                      separators=(',', ': '), cls=EntityEncoder)