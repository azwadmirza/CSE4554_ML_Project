def read_routes():
    if SOLARIS:
        f = os.popen("netstat -rvn")  # -f inet
    elif FREEBSD:
        f = os.popen("netstat -rnW")  # -W to handle long interface names
    else:
        f = os.popen("netstat -rn")  # -f inet
    ok = 0
    mtu_present = False
    prio_present = False
    refs_present = False
    use_present = False
    routes = []
    pending_if = []
    for line in f.readlines():
        if not line:
            break
        line = line.strip()
        if line.find("----") >= 0:  # a separation line
            continue
        if not ok:
            if line.find("Destination") >= 0:
                ok = 1
                mtu_present = "Mtu" in line
                prio_present = "Prio" in line
                refs_present = "Refs" in line
                use_present = "Use" in line
            continue
        if not line:
            break
        if SOLARIS:
            lspl = line.split()
            if len(lspl) == 10:
                dest, mask, gw, netif, mxfrg, rtt, ref, flg = lspl[:8]
            else:  # missing interface
                dest, mask, gw, mxfrg, rtt, ref, flg = lspl[:7]
                netif = None
        else:
            rt = line.split()
            dest, gw, flg = rt[:3]
            locked = OPENBSD and rt[6] == "L"
            offset = mtu_present + prio_present + refs_present + locked
            offset += use_present
            netif = rt[3 + offset]
        if flg.find("Lc") >= 0:
            continue
        if dest == "default":
            dest = 0
            netmask = 0
        else:
            if SOLARIS:
                netmask = scapy.utils.atol(mask)
            elif "/" in dest:
                dest, netmask = dest.split("/")
                netmask = scapy.utils.itom(int(netmask))
            else:
                netmask = scapy.utils.itom((dest.count(".") + 1) * 8)
            dest += ".0" * (3 - dest.count("."))
            dest = scapy.utils.atol(dest)
        # XXX: TODO: add metrics for unix.py (use -e option on netstat)
        metric = 1
        if "G" not in flg:
            gw = '0.0.0.0'
        if netif is not None:
            try:
                ifaddr = get_if_addr(netif)
                routes.append((dest, netmask, gw, netif, ifaddr, metric))
            except OSError as exc:
                if exc.message == 'Device not configured':
                    # This means the interface name is probably truncated by
                    # netstat -nr. We attempt to guess it's name and if not we
                    # ignore it.
                    guessed_netif = _guess_iface_name(netif)
                    if guessed_netif is not None:
                        ifaddr = get_if_addr(guessed_netif)
                        routes.append((dest, netmask, gw, guessed_netif, ifaddr, metric))  # noqa: E501
                    else:
                        warning("Could not guess partial interface name: %s", netif)  # noqa: E501
                else:
                    raise
        else:
            pending_if.append((dest, netmask, gw))
    f.close()

    # On Solaris, netstat does not provide output interfaces for some routes
    # We need to parse completely the routing table to route their gw and
    # know their output interface
    for dest, netmask, gw in pending_if:
        gw_l = scapy.utils.atol(gw)
        max_rtmask, gw_if, gw_if_addr, = 0, None, None
        for rtdst, rtmask, _, rtif, rtaddr in routes[:]:
            if gw_l & rtmask == rtdst:
                if rtmask >= max_rtmask:
                    max_rtmask = rtmask
                    gw_if = rtif
                    gw_if_addr = rtaddr
        # XXX: TODO add metrics
        metric = 1
        if gw_if:
            routes.append((dest, netmask, gw, gw_if, gw_if_addr, metric))
        else:
            warning("Did not find output interface to reach gateway %s", gw)

    return routes