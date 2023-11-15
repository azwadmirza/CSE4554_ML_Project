def read_routes():
    # type: () -> List[Tuple[int, int, str, str, str, int]]
    """Return a list of IPv4 routes than can be used by Scapy.

    This function parses netstat.
    """
    if SOLARIS:
        f = os.popen("netstat -rvn -f inet")
    elif FREEBSD:
        f = os.popen("netstat -rnW -f inet")  # -W to show long interface names
    else:
        f = os.popen("netstat -rn -f inet")
    ok = 0
    mtu_present = False
    prio_present = False
    refs_present = False
    use_present = False
    routes = []  # type: List[Tuple[int, int, str, str, str, int]]
    pending_if = []  # type: List[Tuple[int, int, str]]
    for line in f.readlines():
        if not line:
            break
        line = line.strip().lower()
        if line.find("----") >= 0:  # a separation line
            continue
        if not ok:
            if line.find("destination") >= 0:
                ok = 1
                mtu_present = "mtu" in line
                prio_present = "prio" in line
                refs_present = "ref" in line  # There is no s on Solaris
                use_present = "use" in line or "nhop" in line
            continue
        if not line:
            break
        rt = line.split()
        if SOLARIS:
            dest_, netmask_, gw, netif = rt[:4]
            flg = rt[4 + mtu_present + refs_present]
        else:
            dest_, gw, flg = rt[:3]
            locked = OPENBSD and rt[6] == "l"
            offset = mtu_present + prio_present + refs_present + locked
            offset += use_present
            netif = rt[3 + offset]
        if flg.find("lc") >= 0:
            continue
        elif dest_ == "default":
            dest = 0
            netmask = 0
        elif SOLARIS:
            dest = scapy.utils.atol(dest_)
            netmask = scapy.utils.atol(netmask_)
        else:
            if "/" in dest_:
                dest_, netmask_ = dest_.split("/")
                netmask = scapy.utils.itom(int(netmask_))
            else:
                netmask = scapy.utils.itom((dest_.count(".") + 1) * 8)
            dest_ += ".0" * (3 - dest_.count("."))
            dest = scapy.utils.atol(dest_)
        # XXX: TODO: add metrics for unix.py (use -e option on netstat)
        metric = 1
        if "g" not in flg:
            gw = '0.0.0.0'
        if netif is not None:
            from scapy.arch import get_if_addr
            try:
                ifaddr = get_if_addr(netif)
                routes.append((dest, netmask, gw, netif, ifaddr, metric))
            except OSError as exc:
                if 'Device not configured' in str(exc):
                    # This means the interface name is probably truncated by
                    # netstat -nr. We attempt to guess it's name and if not we
                    # ignore it.
                    guessed_netif = _guess_iface_name(netif)
                    if guessed_netif is not None:
                        ifaddr = get_if_addr(guessed_netif)
                        routes.append((dest, netmask, gw, guessed_netif, ifaddr, metric))  # noqa: E501
                    else:
                        log_runtime.info(
                            "Could not guess partial interface name: %s",
                            netif
                        )
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
        max_rtmask, gw_if, gw_if_addr = 0, None, None
        for rtdst, rtmask, _, rtif, rtaddr, _ in routes[:]:
            if gw_l & rtmask == rtdst:
                if rtmask >= max_rtmask:
                    max_rtmask = rtmask
                    gw_if = rtif
                    gw_if_addr = rtaddr
        # XXX: TODO add metrics
        metric = 1
        if gw_if and gw_if_addr:
            routes.append((dest, netmask, gw, gw_if, gw_if_addr, metric))
        else:
            warning("Did not find output interface to reach gateway %s", gw)

    return routes