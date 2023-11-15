    def __init__(self,
                 agent: 'EthereumContractAgent',
                 event_name: str,
                 from_block: int,
                 to_block: int = None,  # defaults to latest block
                 max_blocks_per_call: int = DEFAULT_MAX_BLOCKS_PER_CALL,
                 **argument_filters):
        self.event_filter = agent.events[event_name]
        self.from_block = from_block
        self.to_block = to_block if to_block is not None else agent.blockchain.client.block_number
        # validity check of block range
        if self.to_block < self.from_block:
            raise ValueError(f"Invalid events block range: to_block {self.to_block} must be greater than or equal "
                             f"to from_block {self.from_block}")

        self.max_blocks_per_call = max_blocks_per_call
        self.argument_filters = argument_filters