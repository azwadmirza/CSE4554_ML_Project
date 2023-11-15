    def __init__(self,
                 event_name: str,
                 event_args_config: Dict[str, tuple],
                 argument_filters: Dict[str, str],
                 contract_agent: ContractAgents):
        super().__init__()
        self.event_name = event_name
        self.contract_agent = contract_agent

        # this way we don't have to deal with 'latest' at all
        self.filter_current_from_block = self.contract_agent.blockchain.client.block_number
        self.filter_arguments = argument_filters
        self.event_args_config = event_args_config