def get_connection(module):
    global _DEVICE_CONNECTION
    if not _DEVICE_CONNECTION:
        load_params(module)
        if 'transport' not in module.params:
            conn = Cli(module)
        elif module.params['transport'] == 'eapi':
            conn = Eapi(module)
        else:
            conn = Cli(module)
        _DEVICE_CONNECTION = conn
    return _DEVICE_CONNECTION