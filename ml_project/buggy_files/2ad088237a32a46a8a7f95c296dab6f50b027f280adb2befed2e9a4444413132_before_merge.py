def get_dns_servers(interface='Local Area Connection'):
    '''
    Return a list of the configured DNS servers of the specified interface

    CLI Example:

    .. code-block:: bash

        salt '*' win_dns_client.get_dns_servers 'Local Area Connection'
    '''
    # remove any escape characters
    interface = interface.split('\\')
    interface = ''.join(interface)

    with salt.utils.winapi.Com():
        c = wmi.WMI()
        for iface in c.Win32_NetworkAdapter(NetEnabled=True):
            if interface == iface.NetConnectionID:
                iface_config = c.Win32_NetworkAdapterConfiguration(Index=iface.Index).pop()
                try:
                    return list(iface_config.DNSServerSearchOrder)
                except TypeError:
                    return []
    log.debug('Interface "%s" not found', interface)
    return False