    def __getitem__(self, event_name: str):
        event_method = self.__get_web3_event_by_name(event_name)

        def wrapper(from_block=None, to_block=None, **argument_filters):

            if from_block is None:
                from_block = 0  # TODO: we can do better. Get contract creation block.
            if to_block is None:
                to_block = 'latest'

            entries = event_method.getLogs(fromBlock=from_block, toBlock=to_block, argument_filters=argument_filters)
            for entry in entries:
                yield EventRecord(entry)
        return wrapper