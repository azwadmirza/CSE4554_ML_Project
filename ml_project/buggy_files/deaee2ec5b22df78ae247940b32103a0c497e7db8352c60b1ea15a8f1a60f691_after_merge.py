def parse_yaml(text, path, typ="safe"):
    yaml = YAML(typ=typ)
    try:
        with reraise(_YAMLError, YAMLFileCorruptedError(path)):
            return yaml.load(text) or {}
    except DuplicateKeyError as exc:
        # NOTE: unfortunately this one doesn't inherit from YAMLError, so we
        # have to catch it by-hand. See
        # https://yaml.readthedocs.io/en/latest/api.html#duplicate-keys
        raise YAMLError(path, exc.problem)