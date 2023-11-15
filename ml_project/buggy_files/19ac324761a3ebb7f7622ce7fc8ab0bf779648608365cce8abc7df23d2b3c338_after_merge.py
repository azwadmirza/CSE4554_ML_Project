def serialize_string(dumper, data):
    """ Ensure boolean-like strings are quoted in the output and escape $ characters """
    representer = dumper.represent_str if six.PY3 else dumper.represent_unicode

    if isinstance(data, six.binary_type):
        data = data.decode('utf-8')

    data = data.replace('$', '$$')

    if data.lower() in ('y', 'n', 'yes', 'no', 'on', 'off', 'true', 'false'):
        # Empirically only y/n appears to be an issue, but this might change
        # depending on which PyYaml version is being used. Err on safe side.
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
    return representer(data)