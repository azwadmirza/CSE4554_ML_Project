def is_cliconf(module):
    capabilities = get_device_capabilities(module)
    return True if capabilities.get('network_api') == 'cliconf' else False