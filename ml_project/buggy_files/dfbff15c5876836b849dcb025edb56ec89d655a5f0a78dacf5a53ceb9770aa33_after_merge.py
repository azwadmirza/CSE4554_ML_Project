def get_ips(v6=False):
    """Returns all available IPs matching to interfaces, using the windows system.
    Should only be used as a WinPcapy fallback."""
    res = {}
    for descr, ipaddr in exec_query(['Get-WmiObject',
                                     'Win32_NetworkAdapterConfiguration'],
                                    ['Description', 'IPAddress']):
        if ipaddr.strip():
            # This requires lots of stripping
            ip_string = ipaddr.split(",", 1)[v6].strip('{}').strip()
            res[descr] = [ip.strip() for ip in ip_string.split(",")]
    return res