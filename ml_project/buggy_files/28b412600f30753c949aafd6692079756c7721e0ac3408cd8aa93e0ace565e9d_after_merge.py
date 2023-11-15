    def __init__(self, origin, rdclass=dns.rdataclass.IN, relativize=True):
        """Initialize a zone object.

        @param origin: The origin of the zone.
        @type origin: dns.name.Name object
        @param rdclass: The zone's rdata class; the default is class IN.
        @type rdclass: int"""

        if origin is not None:
            if isinstance(origin, string_types):
                origin = dns.name.from_text(origin)
            elif not isinstance(origin, dns.name.Name):
                raise ValueError("origin parameter must be convertable to a "
                                 "DNS name")
            if not origin.is_absolute():
                raise ValueError("origin parameter must be an absolute name")
        self.origin = origin
        self.rdclass = rdclass
        self.nodes = {}
        self.relativize = relativize