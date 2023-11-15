def get_if_raw_addr(ifname):
    """Returns the IPv4 address configured on 'ifname', packed with inet_pton."""  # noqa: E501

    ifname = network_name(ifname)

    # Get ifconfig output
    subproc = subprocess.Popen(
        [conf.prog.ifconfig, ifname],
        close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = subproc.communicate()
    if subproc.returncode:
        warning("Failed to execute ifconfig: (%s)", plain_str(stderr))
        return b"\0\0\0\0"
    # Get IPv4 addresses

    addresses = [
        line.strip() for line in plain_str(stdout).splitlines()
        if "inet " in line
    ]

    if not addresses:
        warning("No IPv4 address found on %s !", ifname)
        return b"\0\0\0\0"

    # Pack the first address
    address = addresses[0].split(' ')[1]
    if '/' in address:  # NetBSD 8.0
        address = address.split("/")[0]
    return socket.inet_pton(socket.AF_INET, address)