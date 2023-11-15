def is_netconf(module):
    capabilities = get_device_capabilities(module)
    network_api = capabilities.get('network_api')
    if network_api == 'netconf':
        if not HAS_NCCLIENT:
            module.fail_json(msg='ncclient is not installed')
        if not HAS_XML:
            module.fail_json(msg='lxml is not installed')
        return True

    return False