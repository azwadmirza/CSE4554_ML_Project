def compile_filter(filter_exp, iface=None, linktype=None,
                   promisc=False):
    """Asks libpcap to parse the filter, then build the matching
    BPF bytecode.

    :param iface: if provided, use the interface to compile
    :param linktype: if provided, use the linktype to compile
    """
    try:
        from scapy.libs.winpcapy import (
            PCAP_ERRBUF_SIZE,
            pcap_open_live,
            pcap_compile,
            pcap_compile_nopcap,
            pcap_close
        )
        from scapy.libs.structures import bpf_program
    except ImportError:
        raise Scapy_Exception(
            "libpcap is not available. Cannot compile filter !"
        )
    root = WINDOWS or (os.geteuid() == 0)
    from ctypes import create_string_buffer
    bpf = bpf_program()
    bpf_filter = create_string_buffer(filter_exp.encode("utf8"))
    if not linktype:
        # Try to guess linktype to avoid root
        if not iface:
            if not conf.iface:
                raise Scapy_Exception(
                    "Please provide an interface or linktype!"
                )
            if WINDOWS:
                iface = conf.iface.pcap_name
            else:
                iface = conf.iface
        # Try to guess linktype to avoid requiring root
        try:
            arphd = get_if_raw_hwaddr(iface)[0]
            linktype = ARPHRD_TO_DLT.get(arphd)
        except Exception:
            # Failed to use linktype: use the interface
            if not root:
                raise Scapy_Exception(
                    "Please provide a valid interface or linktype!"
                )
    if linktype is not None:
        ret = pcap_compile_nopcap(
            MTU, linktype, ctypes.byref(bpf), bpf_filter, 0, -1
        )
    elif iface:
        if not root:
            raise OSError(
                "Compiling using an interface requires root."
            )
        err = create_string_buffer(PCAP_ERRBUF_SIZE)
        iface = create_string_buffer(iface.encode("utf8"))
        pcap = pcap_open_live(
            iface, MTU, promisc, 0, err
        )
        ret = pcap_compile(
            pcap, ctypes.byref(bpf), bpf_filter, 0, -1
        )
        pcap_close(pcap)
    if ret == -1:
        raise Scapy_Exception(
            "Failed to compile filter expression %s (%s)" % (filter_exp, ret)
        )
    if conf.use_pypy and sys.pypy_version_info <= (7, 3, 0):
        # PyPy < 7.3.0 has a broken behavior
        # https://bitbucket.org/pypy/pypy/issues/3114
        return struct.pack(
            'HL',
            bpf.bf_len, ctypes.addressof(bpf.bf_insns.contents)
        )
    return bpf