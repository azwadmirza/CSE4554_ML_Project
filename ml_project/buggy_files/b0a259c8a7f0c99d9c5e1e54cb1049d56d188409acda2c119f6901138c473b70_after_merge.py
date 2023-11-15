    def __init__(self,
                 transport: TransportAPI,
                 base_protocol: BaseP2PProtocol,
                 protocols: Sequence[ProtocolAPI],
                 token: CancelToken = None,
                 max_queue_size: int = 4096) -> None:
        if token is None:
            loop = None
        else:
            loop = token.loop
        base_token = CancelToken(f'multiplexer[{transport.remote}]', loop=loop)

        if token is None:
            self.cancel_token = base_token
        else:
            self.cancel_token = base_token.chain(token)

        self._transport = transport
        # the base `p2p` protocol instance.
        self._base_protocol = base_protocol

        # the sub-protocol instances
        self._protocols = protocols

        # Lock to ensure that multiple call sites cannot concurrently stream
        # messages.
        self._multiplex_lock = asyncio.Lock()

        # Lock management on a per-protocol basis to ensure we only have one
        # stream consumer for each protocol.
        self._protocol_locks = {
            type(protocol): asyncio.Lock()
            for protocol
            in self.get_protocols()
        }

        # Each protocol gets a queue where messages for the individual protocol
        # are placed when streamed from the transport
        self._protocol_queues = {
            type(protocol): asyncio.Queue(max_queue_size)
            for protocol
            in self.get_protocols()
        }

        self._msg_counts = collections.defaultdict(int)