def json_dump(object):
    return ensure_text_type(json.dumps(object, indent=2, sort_keys=True,
                                       separators=(',', ': '), cls=EntityEncoder))