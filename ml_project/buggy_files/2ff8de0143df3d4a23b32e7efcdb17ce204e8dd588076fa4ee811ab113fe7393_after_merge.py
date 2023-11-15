def coerce_type(module, value):
    # If our value is already None we can just return directly
    if value is None:
        return value

    yaml_ish = bool((
        value.startswith('{') and value.endswith('}')
    ) or (
        value.startswith('[') and value.endswith(']'))
    )
    if yaml_ish:
        if not HAS_YAML:
            module.fail_json(msg="yaml is not installed, try 'pip install pyyaml'")
        return yaml.safe_load(value)
    elif value.lower in ('true', 'false', 't', 'f'):
        return {'t': True, 'f': False}[value[0].lower()]
    try:
        return int(value)
    except ValueError:
        pass
    return value