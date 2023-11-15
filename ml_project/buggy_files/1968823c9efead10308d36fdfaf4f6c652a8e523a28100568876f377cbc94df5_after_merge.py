def get_existing(module):
    existing = []
    netcfg = CustomNetworkConfig(indent=2, contents=get_config(module))

    if module.params['mode'] == 'maintenance':
        parents = ['configure maintenance profile maintenance-mode']
    else:
        parents = ['configure maintenance profile normal-mode']

    config = netcfg.get_section(parents)
    if config:
        existing = config.splitlines()
        existing = [cmd.strip() for cmd in existing]
        existing.pop(0)

    return existing