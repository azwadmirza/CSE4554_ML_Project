def stdout_json(d):
    import json
    from .._vendor.auxlib.entity import EntityEncoder
    json.dump(d, sys.stdout, indent=2, sort_keys=True, cls=EntityEncoder)
    sys.stdout.write('\n')