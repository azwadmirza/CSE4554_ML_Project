def get_dns_config(interface='Local Area Connection'):
    '''
    Get the type of DNS configuration (dhcp / static)

    CLI Example:

    .. code-block:: bash

        salt '*' win_dns_client.get_dns_config 'Local Area Connection'
    '''
    # remove any escape characters
    interface = interface.split('\\')
    interface = ''.join(interface)

    with salt.utils.winapi.Com():
        c = wmi.WMI()
        for iface in c.Win32_NetworkAdapterConfiguration(IPEnabled=1):
            if interface == iface.Description:
                return iface.DHCPEnabled