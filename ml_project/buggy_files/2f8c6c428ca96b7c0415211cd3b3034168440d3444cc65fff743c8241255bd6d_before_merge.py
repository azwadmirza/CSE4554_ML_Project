def _set_conf_sockets():
    """Populate the conf.L2Socket and conf.L3Socket
    according to the various use_* parameters
    """
    if conf.use_bpf and not DARWIN:
        Interceptor.set_from_hook(conf, "use_bpf", False)
        raise ScapyInvalidPlatformException("Darwin (OSX) only !")
    if conf.use_winpcapy and not WINDOWS:
        Interceptor.set_from_hook(conf, "use_winpcapy", False)
        raise ScapyInvalidPlatformException("Windows only !")
    # we are already in an Interceptor hook, use Interceptor.set_from_hook
    if conf.use_pcap or conf.use_dnet or conf.use_winpcapy:
        try:
            from scapy.arch.pcapdnet import L2pcapListenSocket, L2pcapSocket, \
                L3pcapSocket
        except ImportError:
            warning("No pcap provider available ! pcap won't be used")
            Interceptor.set_from_hook(conf, "use_winpcapy", False)
            Interceptor.set_from_hook(conf, "use_pcap", False)
        else:
            conf.L2listen = L2pcapListenSocket
            conf.L2socket = L2pcapSocket
            conf.L3socket = L3pcapSocket
            return
    if conf.use_bpf:
        from scapy.arch.bpf.supersocket import L2bpfListenSocket, \
            L2bpfSocket, L3bpfSocket
        conf.L2listen = L2bpfListenSocket
        conf.L2socket = L2bpfSocket
        conf.L3socket = L3bpfSocket
        return
    if LINUX:
        from scapy.arch.linux import L3PacketSocket, L2Socket, L2ListenSocket
        conf.L3socket = L3PacketSocket
        conf.L2socket = L2Socket
        conf.L2listen = L2ListenSocket
        return
    if WINDOWS:  # Should have been conf.use_winpcapy
        from scapy.arch.windows import _NotAvailableSocket
        conf.L2socket = _NotAvailableSocket
        conf.L2listen = _NotAvailableSocket
        conf.L3socket = _NotAvailableSocket
        return
    from scapy.supersocket import L3RawSocket
    conf.L3socket = L3RawSocket