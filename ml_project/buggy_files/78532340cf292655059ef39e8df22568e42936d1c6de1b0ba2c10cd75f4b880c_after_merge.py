    def __init__(self, circuit_id, sock_addr, rendezvous_relay=False, mid=None):
        """
        @type sock_addr: (str, int)
        @type circuit_id: int
        @return:
        """

        self.sock_addr = sock_addr
        self.circuit_id = circuit_id
        self.creation_time = time.time()
        self.last_incoming = time.time()
        self.bytes_up = self.bytes_down = 0
        self.rendezvous_relay = rendezvous_relay
        self.mid = mid