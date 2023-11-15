    def _check_and_send(self) -> None:
        """Check and send all pending/queued messages that are not waiting on retry timeout

        After composing the to-be-sent message, also message queue from messages that are not
        present in the respective SendMessageEvent queue anymore
        """
        if not self.transport.greenlet:
            self.log.warning("Can't retry", reason="Transport not yet started")
            return
        if self.transport._stop_event.ready():
            self.log.warning("Can't retry", reason="Transport stopped")
            return

        assert self._lock.locked(), "RetryQueue lock must be held while messages are being sent"

        # On startup protocol messages must be sent only after the monitoring
        # services are updated. For more details refer to the method
        # `RaidenService._initialize_monitoring_services_queue`
        if self.transport._prioritize_broadcast_messages:
            self.transport._broadcast_queue.join()

        self.log.debug("Retrying message(s)", receiver=to_checksum_address(self.receiver))
        status = self.transport._address_mgr.get_address_reachability(self.receiver)
        if status is not AddressReachability.REACHABLE:
            # if partner is not reachable, return
            self.log.debug(
                "Partner not reachable. Skipping.",
                partner=to_checksum_address(self.receiver),
                status=status,
            )
            return

        def message_is_in_queue(message_data: _RetryQueue._MessageData) -> bool:
            if message_data.queue_identifier not in self.transport._queueids_to_queues:
                # The Raiden queue for this queue identifier has been removed
                return False
            return any(
                isinstance(message_data.message, RetrieableMessage)
                and send_event.message_identifier == message_data.message.message_identifier
                for send_event in self.transport._queueids_to_queues[message_data.queue_identifier]
            )

        message_texts: List[str] = list()
        for message_data in self._message_queue[:]:
            # Messages are sent on two conditions:
            # - Non-retryable (e.g. Delivered)
            #   - Those are immediately remove from the local queue since they are only sent once
            # - Retryable
            #   - Those are retried according to their retry generator as long as they haven't been
            #     removed from the Raiden queue
            remove = False
            if isinstance(message_data.message, (Delivered, Ping, Pong)):
                # e.g. Delivered, send only once and then clear
                # TODO: Is this correct? Will a missed Delivered be 'fixed' by the
                #       later `Processed` message?
                remove = True
                message_texts.append(message_data.text)
            elif not message_is_in_queue(message_data):
                remove = True
                self.log.debug(
                    "Stopping message send retry",
                    queue=message_data.queue_identifier,
                    message=message_data.message,
                    reason="Message was removed from queue or queue was removed",
                )
            else:
                # The message is still eligible for retry, consult the expiration generator if
                # it should be retried now
                if next(message_data.expiration_generator):
                    message_texts.append(message_data.text)

            if remove:
                self._message_queue.remove(message_data)

        if message_texts:
            self.log.debug(
                "Send", receiver=to_checksum_address(self.receiver), messages=message_texts
            )
            self.transport._send_raw(self.receiver, "\n".join(message_texts))