    def _collect_internal(self) -> None:
        from_block = self.filter_current_from_block
        to_block = self.contract_agent.blockchain.client.block_number
        if from_block >= to_block:
            # we've already checked the latest block and waiting for a new block
            # nothing to see here
            return

        events_throttler = ContractEventsThrottler(agent=self.contract_agent,
                                                   event_name=self.event_name,
                                                   from_block=from_block,
                                                   to_block=to_block,
                                                   **self.filter_arguments)
        for event_record in events_throttler:
            self._event_occurred(event_record.raw_event)

        # update last block checked for the next round - from/to block range is inclusive
        self.filter_current_from_block = to_block + 1