    def __init__(self, filename, fdesc, magic):
        RawPcapReader.__init__(self, filename, fdesc, magic)
        try:
            self.LLcls = conf.l2types[self.linktype]
        except KeyError:
            warning("PcapReader: unknown LL type [%i]/[%#x]. Using Raw packets" % (self.linktype, self.linktype))  # noqa: E501
            from scapy.packet import Raw
            self.LLcls = conf.raw_layer or Raw