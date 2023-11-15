def is_cliconf(module):
    capabilities = get_device_capabilities(module)
    network_api = capabilities.get('network_api')
    if network_api not in ('cliconf', 'netconf'):
        module.fail_json(msg=('unsupported network_api: {!s}'.format(network_api)))
        return False

    if network_api == 'cliconf':
        return True

    return False