def get_ips(v6=False):
    """Returns all available IPs matching to interfaces, using the windows system.
    Should only be used as a WinPcapy fallback."""
    res = {}
    for descr, ipaddr in exec_query(['Get-WmiObject',
                                     'Win32_NetworkAdapterConfiguration'],
                                    ['Description', 'IPAddress']):
        if ipaddr.strip():
            res[descr] = ipaddr.split(",", 1)[v6].strip('{}').strip()
    return res