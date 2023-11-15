    def initialize(self, metrics_prefix: str, registry: CollectorRegistry) -> None:
        super().initialize(metrics_prefix=metrics_prefix, registry=registry)

        missing_commitments = self.contract_agent.get_missing_commitments(checksum_address=self.staker_address)
        if missing_commitments == 0:
            # has either already committed to this period or the next period

            # use local event filter for initial data
            last_committed_period = self.contract_agent.get_last_committed_period(staker_address=self.staker_address)
            arg_filters = {'staker': self.staker_address, 'period': last_committed_period}
            latest_block = self.contract_agent.blockchain.client.block_number
            previous_period = self.contract_agent.get_current_period() - 1  # just in case
            # we estimate the block number for the previous period to start search from since either
            # - commitment made during previous period for current period, OR
            # - commitment made during current period for next period
            block_number_for_previous_period = estimate_block_number_for_period(
                period=previous_period,
                seconds_per_period=self.contract_agent.staking_parameters()[0],
                latest_block=latest_block)

            events_throttler = ContractEventsThrottler(agent=self.contract_agent,
                                                       event_name=self.event_name,
                                                       from_block=block_number_for_previous_period,
                                                       to_block=latest_block,
                                                       **arg_filters)
            for event_record in events_throttler:
                self._event_occurred(event_record.raw_event)