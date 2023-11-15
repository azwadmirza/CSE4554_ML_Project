    def __init__(self, iface=None, type=ETH_P_ALL, promisc=None, filter=None,
                 nofilter=0, monitor=False):
        self.fd_flags = None
        self.assigned_interface = None

        # SuperSocket mandatory variables
        if promisc is None:
            self.promisc = conf.sniff_promisc
        else:
            self.promisc = promisc

        self.iface = network_name(iface or conf.iface)

        # Get the BPF handle
        (self.ins, self.dev_bpf) = get_dev_bpf()
        self.outs = self.ins

        # Set the BPF buffer length
        try:
            fcntl.ioctl(self.ins, BIOCSBLEN, struct.pack('I', BPF_BUFFER_LENGTH))  # noqa: E501
        except IOError:
            raise Scapy_Exception("BIOCSBLEN failed on /dev/bpf%i" %
                                  self.dev_bpf)

        # Assign the network interface to the BPF handle
        try:
            fcntl.ioctl(self.ins, BIOCSETIF, struct.pack("16s16x", self.iface.encode()))  # noqa: E501
        except IOError:
            raise Scapy_Exception("BIOCSETIF failed on %s" % self.iface)
        self.assigned_interface = self.iface

        # Set the interface into promiscuous
        if self.promisc:
            self.set_promisc(1)

        # Set the interface to monitor mode
        # Note: - trick from libpcap/pcap-bpf.c - monitor_mode()
        #       - it only works on OS X 10.5 and later
        if DARWIN and monitor:
            dlt_radiotap = struct.pack('I', DLT_IEEE802_11_RADIO)
            try:
                fcntl.ioctl(self.ins, BIOCSDLT, dlt_radiotap)
            except IOError:
                raise Scapy_Exception("Can't set %s into monitor mode!" %
                                      self.iface)

        # Don't block on read
        try:
            fcntl.ioctl(self.ins, BIOCIMMEDIATE, struct.pack('I', 1))
        except IOError:
            raise Scapy_Exception("BIOCIMMEDIATE failed on /dev/bpf%i" %
                                  self.dev_bpf)

        # Scapy will provide the link layer source address
        # Otherwise, it is written by the kernel
        try:
            fcntl.ioctl(self.ins, BIOCSHDRCMPLT, struct.pack('i', 1))
        except IOError:
            raise Scapy_Exception("BIOCSHDRCMPLT failed on /dev/bpf%i" %
                                  self.dev_bpf)

        # Configure the BPF filter
        if not nofilter:
            if conf.except_filter:
                if filter:
                    filter = "(%s) and not (%s)" % (filter, conf.except_filter)
                else:
                    filter = "not (%s)" % conf.except_filter
            if filter is not None:
                try:
                    attach_filter(self.ins, filter, self.iface)
                except ImportError as ex:
                    warning("Cannot set filter: %s" % ex)

        # Set the guessed packet class
        self.guessed_cls = self.guess_cls()