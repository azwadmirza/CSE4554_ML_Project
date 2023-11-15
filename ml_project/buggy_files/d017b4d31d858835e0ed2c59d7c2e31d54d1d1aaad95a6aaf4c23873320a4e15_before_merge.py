    def __init__(self,
                 event_name: str,
                 event_args_config: Dict[str, tuple],
                 argument_filters: Dict[str, str],
                 contract_agent: ContractAgents):
        super().__init__()
        self.event_name = event_name
        self.contract_agent = contract_agent
        self.event_filter = contract_agent.contract.events[event_name].createFilter(fromBlock='latest',
                                                                                    argument_filters=argument_filters)
        self.event_args_config = event_args_config