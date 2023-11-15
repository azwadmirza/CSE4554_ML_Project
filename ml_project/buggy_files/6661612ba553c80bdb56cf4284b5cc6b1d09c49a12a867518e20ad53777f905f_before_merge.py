    def __init__(self,
                 agent: 'EthereumContractAgent',
                 event_name: str,
                 from_block: int,
                 to_block: int = None,  # defaults to latest block
                 max_blocks_per_call: int = DEFAULT_MAX_BLOCKS_PER_CALL,
                 **argument_filters):
        if not agent:
            raise ValueError(f"Contract agent must be provided")
        if not event_name:
            raise ValueError(f"Event name must be provided")

        self.event_filter = agent.events[event_name]
        self.from_block = from_block
        self.to_block = to_block if to_block else agent.blockchain.client.block_number
        # validity check of block range
        if to_block <= from_block:
            raise ValueError(f"Invalid block range provided ({from_block} - {to_block})")

        self.max_blocks_per_call = max_blocks_per_call
        self.argument_filters = argument_filters