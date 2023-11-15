def parse_yaml(text, path, typ="safe"):
    yaml = YAML(typ=typ)
    with reraise(YAMLError, YAMLFileCorruptedError(path)):
        return yaml.load(text) or {}