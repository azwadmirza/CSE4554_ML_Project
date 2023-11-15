    def __init__(self, circuit_id, goal_hops=0, first_hop=None, proxy=None,
                 ctype=CIRCUIT_TYPE_DATA, callback=None, required_exit=None,
                 mid=None, info_hash=None):
        """
        Instantiate a new Circuit data structure
        :type proxy: TunnelCommunity
        :param int circuit_id: the id of the candidate circuit
        :param (str, int) first_hop: the first hop of the circuit
        :return: Circuit
        """

        from Tribler.community.tunnel.hidden_community import HiddenTunnelCommunity
        assert isinstance(circuit_id, long)
        assert isinstance(goal_hops, int)
        assert proxy is None or isinstance(proxy, HiddenTunnelCommunity)
        assert first_hop is None or isinstance(first_hop, tuple) and isinstance(
            first_hop[0], basestring) and isinstance(first_hop[1], int)

        self._broken = False
        self._hops = []

        self.circuit_id = circuit_id
        self.first_hop = first_hop
        self.goal_hops = goal_hops
        self.creation_time = time.time()
        self.last_incoming = time.time()
        self.unverified_hop = None
        self.bytes_up = self.bytes_down = 0

        self.proxy = proxy
        self.ctype = ctype
        self.callback = callback
        self.required_exit = required_exit
        self.mid = mid
        self.hs_session_keys = None
        self.info_hash = info_hash

        self._logger = logging.getLogger(self.__class__.__name__)