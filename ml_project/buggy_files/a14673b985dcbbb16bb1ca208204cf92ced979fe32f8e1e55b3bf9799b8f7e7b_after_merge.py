    def add_peer(self, addr):
        """ Add a peer address from 3rd source (not tracker, not DHT) to this download.
        @param (hostname_ip,port) tuple
        """
        self.get_handle().addCallback(lambda handle: handle.connect_peer(addr, 0))