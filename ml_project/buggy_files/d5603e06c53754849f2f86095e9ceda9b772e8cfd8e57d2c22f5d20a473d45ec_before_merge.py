def get_if_raw_hwaddr(ifname):
    """Returns the packed MAC address configured on 'ifname'."""

    NULL_MAC_ADDRESS = b'\x00' * 6

    ifname = network_name(ifname)
    # Handle the loopback interface separately
    if ifname == conf.loopback_name:
        return (ARPHDR_LOOPBACK, NULL_MAC_ADDRESS)

    # Get ifconfig output
    subproc = subprocess.Popen(
        [conf.prog.ifconfig, ifname],
        close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = subproc.communicate()
    if subproc.returncode:
        raise Scapy_Exception("Failed to execute ifconfig: (%s)" %
                              (plain_str(stderr)))

    # Get MAC addresses
    addresses = [
        line.strip() for line in plain_str(stdout).splitlines() if (
            "ether" in line or "lladdr" in line or "address" in line
        )
    ]
    if not addresses:
        raise Scapy_Exception("No MAC address found on %s !" % ifname)

    # Pack and return the MAC address
    mac = addresses[0].split(' ')[1]
    mac = [chr(int(b, 16)) for b in mac.split(':')]
    return (ARPHDR_ETHER, ''.join(mac))