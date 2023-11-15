    def __init__(
            self,
            chain: SubstrateChain,
            greenlet_manager: GreenletManager,
            msg_aggregator: MessagesAggregator,
            connect_at_start: Sequence[NodeName],
            connect_on_startup: bool,
            own_rpc_endpoint: str,
    ) -> None:
        """An interface to any Substrate chain supported by Rotki.

        It uses Polkascan py-substrate-interface for interacting with the
        substrate blockchains and the Subscan API as a chain explorer.

        Official substrate chains documentation:
        https://substrate.dev/rustdocs/v2.0.0/sc_service/index.html
        https://guide.kusama.network/docs/en/kusama-index
        https://wiki.polkadot.network/en/

        External Address Format (SS58) documentation:
        https://github.com/paritytech/substrate/wiki/External-Address-Format-(SS58)

        Polkascan py-scale-codec:
        https://github.com/polkascan/py-scale-codec/tree/master

        Polkascan py-substrate-interface:
        https://github.com/polkascan/py-substrate-interface
        https://polkascan.github.io/py-substrate-interface/base.html

        Subscan API documentation:
        https://docs.api.subscan.io
        """
        if chain not in SubstrateChain:
            raise AttributeError(f'Unexpected SubstrateManager chain: {chain}')

        log.debug(f'Initializing {chain} manager')
        self.chain = chain
        self.greenlet_manager = greenlet_manager
        self.msg_aggregator = msg_aggregator
        self.connect_at_start = connect_at_start
        self.own_rpc_endpoint = own_rpc_endpoint
        self.available_node_attributes_map: DictNodeNameNodeAttributes = {}
        self.available_nodes_call_order: NodesCallOrder = []
        self.chain_properties: SubstrateChainProperties
        if connect_on_startup and len(connect_at_start) != 0:
            self.attempt_connections()
        else:
            log.warning(
                f"{self.chain} manager won't attempt to connect to nodes",
                connect_at_start=connect_at_start,
                connect_on_startup=connect_on_startup,
                own_rpc_endpoint=own_rpc_endpoint,
            )