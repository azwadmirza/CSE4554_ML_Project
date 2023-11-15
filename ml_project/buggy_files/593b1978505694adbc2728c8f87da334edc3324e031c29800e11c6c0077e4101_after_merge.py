    def __getattr__(self, event_name: str) -> "ContractEvent":
        if '_events' not in self.__dict__:
            raise NoABIEventsFound(
                "The abi for this contract contains no event definitions. ",
                "Are you sure you provided the correct contract abi?"
            )
        elif event_name not in self.__dict__['_events']:
            raise ABIEventFunctionNotFound(
                "The event '{}' was not found in this contract's abi. ".format(event_name),
                "Are you sure you provided the correct contract abi?"
            )
        else:
            return super().__getattribute__(event_name)