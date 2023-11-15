def __virtual__():
    if not HAS_DEPS:
        return False, 'Could not import couchbase returner; couchbase is not installed.'

    # try to load some faster json libraries. In order of fastest to slowest
    json = salt.utils.import_json()
    couchbase.set_json_converters(json.dumps, json.loads)

    return __virtualname__