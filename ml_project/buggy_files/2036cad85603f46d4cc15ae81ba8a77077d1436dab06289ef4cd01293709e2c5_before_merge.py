    def _poll_until_target(self, target_block_number: BlockNumber) -> None:
        """Poll blockchain events up to `target_block_number`.

        Multiple queries may be necessary on restarts, because the node may
        have been offline for an extend period of time. During normal
        operation, this must not happen, because in this case the node may have
        missed important events, like a channel close, while the transport
        layer is running, this can lead to loss of funds.

        It is very important for `confirmed_target_block_number` to be an
        confirmed block, otherwise reorgs may cause havoc. This is problematic
        since some operations are irreversible, namely sending a balance proof.
        Once a node accepts a deposit, these tokens can be used to do mediated
        transfers, and if a reorg removes the deposit tokens could be lost.

        This function takes care of fetching blocks in batches and confirming
        their result. This is important to keep memory usage low and to speed
        up restarts. Memory usage can get a hit if the node is asleep for a
        long period of time and on the first run, since all the missing
        confirmed blocks have to be fetched before the node is in a working
        state. Restarts get a hit if the node is closed while it was
        synchronizing, without regularly saving that work, if the node is
        killed while synchronizing, it only gets gradually slower.

        Returns:
            int: number of polling queries required to synchronized with
            `target_block_number`.
        """
        msg = (
            f"The blockchain event handler has to be instantiated before the "
            f"alarm task is started. node:{self!r}"
        )
        assert self.blockchain_events, msg
        log.debug(
            "Poll until target",
            target=target_block_number,
            last_fetched_block=self.blockchain_events.last_fetched_block,
        )

        sync_start = datetime.now()

        while self.blockchain_events.last_fetched_block < target_block_number:
            self._log_sync_progress(target_block_number)

            poll_result = self.blockchain_events.fetch_logs_in_batch(target_block_number)
            if poll_result is None:
                # No blocks could be fetched (due to timeout), retry
                continue

            pendingtokenregistration: Dict[
                TokenNetworkAddress, Tuple[TokenNetworkRegistryAddress, TokenAddress]
            ] = dict()

            state_changes: List[StateChange] = list()
            for event in poll_result.events:
                state_changes.extend(
                    blockchainevent_to_statechange(
                        self, event, poll_result.polled_block_number, pendingtokenregistration
                    )
                )

            # On restarts the node has to pick up all events generated since the
            # last run. To do this the node will set the filters' from_block to
            # the value of the latest block number known to have *all* events
            # processed.
            #
            # To guarantee the above the node must either:
            #
            # - Dispatch the state changes individually, leaving the Block
            # state change last, so that it knows all the events for the
            # given block have been processed. On restarts this can result in
            # the same event being processed twice.
            # - Dispatch all the smart contract events together with the Block
            # state change in a single transaction, either all or nothing will
            # be applied, and on a restart the node picks up from where it
            # left.
            #
            # The approach used below is to dispatch the Block and the
            # blockchain events in a single transaction. This is the preferred
            # approach because it guarantees that no events will be missed and
            # it fixes race conditions on the value of the block number value,
            # that can lead to crashes.
            #
            # Example: The user creates a new channel with an initial deposit
            # of X tokens. This is done with two operations, the first is to
            # open the new channel, the second is to deposit the requested
            # tokens in it. Once the node fetches the event for the new channel,
            # it will immediately request the deposit, which leaves a window for
            # a race condition. If the Block state change was not yet
            # processed, the block hash used as the triggering block for the
            # deposit will be off-by-one, and it will point to the block
            # immediately before the channel existed. This breaks a proxy
            # precondition which crashes the client.
            block_state_change = Block(
                block_number=poll_result.polled_block_number,
                gas_limit=poll_result.polled_block_gas_limit,
                block_hash=poll_result.polled_block_hash,
            )
            state_changes.append(block_state_change)

            # It's important to /not/ block here, because this function can
            # be called from the alarm task greenlet, which should not
            # starve. This was a problem when the node decided to send a new
            # transaction, since the proxies block until the transaction is
            # mined and confirmed (e.g. the settle window is over and the
            # node sends the settle transaction).
            self.handle_and_track_state_changes(state_changes)

        sync_end = datetime.now()
        log.debug(
            "Synchronized to a new confirmed block",
            event_filters_qty=len(self.blockchain_events._address_to_filters),
            sync_elapsed=sync_end - sync_start,
        )