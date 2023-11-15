def sniff(count=0, store=True, offline=None, prn=None, lfilter=None,
          L2socket=None, timeout=None, opened_socket=None,
          stop_filter=None, iface=None, started_callback=None,
          session=None, *arg, **karg):
    """Sniff packets and return a list of packets.

    Args:
        count: number of packets to capture. 0 means infinity.
        store: whether to store sniffed packets or discard them
        prn: function to apply to each packet. If something is returned, it
             is displayed.
             --Ex: prn = lambda x: x.summary()
        session: a session = a flow decoder used to handle stream of packets.
                 e.g: IPSession (to defragment on-the-flow) or NetflowSession
        filter: BPF filter to apply.
        lfilter: Python function applied to each packet to determine if
                 further action may be done.
                 --Ex: lfilter = lambda x: x.haslayer(Padding)
        offline: PCAP file (or list of PCAP files) to read packets from,
                 instead of sniffing them
        timeout: stop sniffing after a given time (default: None).
        L2socket: use the provided L2socket (default: use conf.L2listen).
        opened_socket: provide an object (or a list of objects) ready to use
                      .recv() on.
        stop_filter: Python function applied to each packet to determine if
                     we have to stop the capture after this packet.
                     --Ex: stop_filter = lambda x: x.haslayer(TCP)
        iface: interface or list of interfaces (default: None for sniffing
               on all interfaces).
        monitor: use monitor mode. May not be available on all OS
        started_callback: called as soon as the sniffer starts sniffing
                          (default: None).

    The iface, offline and opened_socket parameters can be either an
    element, a list of elements, or a dict object mapping an element to a
    label (see examples below).

    Examples:
      >>> sniff(filter="arp")
      >>> sniff(filter="tcp",
      ...       session=IPSession,  # defragment on-the-flow
      ...       prn=lambda x: x.summary())
      >>> sniff(lfilter=lambda pkt: ARP in pkt)
      >>> sniff(iface="eth0", prn=Packet.summary)
      >>> sniff(iface=["eth0", "mon0"],
      ...       prn=lambda pkt: "%s: %s" % (pkt.sniffed_on,
      ...                                   pkt.summary()))
      >>> sniff(iface={"eth0": "Ethernet", "mon0": "Wifi"},
      ...       prn=lambda pkt: "%s: %s" % (pkt.sniffed_on,
      ...                                   pkt.summary()))
    """
    c = 0
    session = session or DefaultSession
    session = session(prn, store)  # instantiate session
    sniff_sockets = {}  # socket: label dict
    if opened_socket is not None:
        if isinstance(opened_socket, list):
            sniff_sockets.update((s, "socket%d" % i)
                                 for i, s in enumerate(opened_socket))
        elif isinstance(opened_socket, dict):
            sniff_sockets.update((s, label)
                                 for s, label in six.iteritems(opened_socket))
        else:
            sniff_sockets[opened_socket] = "socket0"
    if offline is not None:
        flt = karg.get('filter')

        from scapy.arch.common import TCPDUMP
        if not TCPDUMP and flt is not None:
            message = "tcpdump is not available. Cannot use filter!"
            raise Scapy_Exception(message)

        if isinstance(offline, list):
            sniff_sockets.update((PcapReader(
                fname if flt is None else
                tcpdump(fname, args=["-w", "-", flt], getfd=True)
            ), fname) for fname in offline)
        elif isinstance(offline, dict):
            sniff_sockets.update((PcapReader(
                fname if flt is None else
                tcpdump(fname, args=["-w", "-", flt], getfd=True)
            ), label) for fname, label in six.iteritems(offline))
        else:
            sniff_sockets[PcapReader(
                offline if flt is None else
                tcpdump(offline, args=["-w", "-", flt], getfd=True)
            )] = offline
    if not sniff_sockets or iface is not None:
        if L2socket is None:
            L2socket = conf.L2listen
        if isinstance(iface, list):
            sniff_sockets.update(
                (L2socket(type=ETH_P_ALL, iface=ifname, *arg, **karg), ifname)
                for ifname in iface
            )
        elif isinstance(iface, dict):
            sniff_sockets.update(
                (L2socket(type=ETH_P_ALL, iface=ifname, *arg, **karg), iflabel)
                for ifname, iflabel in six.iteritems(iface)
            )
        else:
            sniff_sockets[L2socket(type=ETH_P_ALL, iface=iface,
                                   *arg, **karg)] = iface
    if timeout is not None:
        stoptime = time.time() + timeout
    remain = None

    # Get select information from the sockets
    _main_socket = next(iter(sniff_sockets))
    read_allowed_exceptions = _main_socket.read_allowed_exceptions
    select_func = _main_socket.select
    # We check that all sockets use the same select(), or raise a warning
    if not all(select_func == sock.select for sock in sniff_sockets):
        warning("Warning: inconsistent socket types ! The used select function"
                "will be the one of the first socket")
    # Now let's build the select function, used later on
    _select = lambda sockets, remain: select_func(sockets, remain)[0]

    try:
        if started_callback:
            started_callback()
        continue_sniff = True
        while sniff_sockets and continue_sniff:
            if timeout is not None:
                remain = stoptime - time.time()
                if remain <= 0:
                    break
            for s in _select(sniff_sockets, remain):
                try:
                    p = s.recv()
                except socket.error as ex:
                    warning("Socket %s failed with '%s' and thus"
                            " will be ignored" % (s, ex))
                    del sniff_sockets[s]
                    continue
                except read_allowed_exceptions:
                    continue
                if p is None:
                    try:
                        if s.promisc:
                            continue
                    except AttributeError:
                        pass
                    del sniff_sockets[s]
                    break
                if lfilter and not lfilter(p):
                    continue
                p.sniffed_on = sniff_sockets[s]
                c += 1
                # on_packet_received handles the prn/storage
                session.on_packet_received(p)
                if stop_filter and stop_filter(p):
                    continue_sniff = False
                    break
                if 0 < count <= c:
                    continue_sniff = False
                    break
    except KeyboardInterrupt:
        pass
    if opened_socket is None:
        for s in sniff_sockets:
            s.close()
    return session.toPacketList()