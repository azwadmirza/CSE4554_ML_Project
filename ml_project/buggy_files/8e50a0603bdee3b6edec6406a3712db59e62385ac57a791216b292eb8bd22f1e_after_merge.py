    def _synchronize_with_blockchain(self) -> None:
        """Prepares the alarm task callback and synchronize with the blockchain
        since the last run.

         Notes about setup order:
         - The filters must be polled after the node state has been primed,
           otherwise the state changes won't have effect.
         - The synchronization must be done before the transport is started, to
           reject messages for closed/settled channels.
        """
        msg = (
            f"Transport must not be started before the node has synchronized "
            f"with the blockchain, otherwise the node may accept transfers to a "
            f"closed channel. node:{self!r}"
        )
        assert not self.transport, msg
        assert self.wal, f"The database must have been initialized. node:{self!r}"

        chain_state = views.state_from_raiden(self)

        # The `Block` state change is dispatched only after all the events for
        # that given block have been processed, filters can be safely installed
        # starting from this position without missing events.
        last_block_number = views.block_number(chain_state)

        filters = smart_contract_filters_from_node_state(
            chain_state,
            self.contract_manager,
            self.default_registry.address,
            self.default_secret_registry.address,
        )
        blockchain_events = BlockchainEvents(
            web3=self.rpc_client.web3,
            chain_id=chain_state.chain_id,
            contract_manager=self.contract_manager,
            last_fetched_block=last_block_number,
            event_filters=filters,
            block_batch_size_config=self.config.blockchain.block_batch_size_config,
        )

        self.last_log_block = last_block_number
        self.last_log_time = time.monotonic()

        latest_block_num = self.rpc_client.block_number()
        latest_confirmed_block_number = BlockNumber(
            max(GENESIS_BLOCK_NUMBER, latest_block_num - self.confirmation_blocks)
        )

        # `blockchain_events` is a requirement for `_poll_until_target`, so it
        # must be set before calling it
        self.blockchain_events = blockchain_events
        self._poll_until_target(latest_confirmed_block_number)

        self.alarm.register_callback(self._callback_new_block)