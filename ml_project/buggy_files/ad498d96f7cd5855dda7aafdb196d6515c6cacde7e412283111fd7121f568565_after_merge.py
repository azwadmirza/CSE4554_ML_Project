    def _check_sigs_and_hashes(
        self, room_version: str, pdus: List[EventBase]
    ) -> List[Deferred]:
        """Checks that each of the received events is correctly signed by the
        sending server.

        Args:
            room_version: The room version of the PDUs
            pdus: the events to be checked

        Returns:
            For each input event, a deferred which:
              * returns the original event if the checks pass
              * returns a redacted version of the event (if the signature
                matched but the hash did not)
              * throws a SynapseError if the signature check failed.
            The deferreds run their callbacks in the sentinel
        """
        deferreds = _check_sigs_on_pdus(self.keyring, room_version, pdus)

        ctx = LoggingContext.current_context()

        def callback(_, pdu: EventBase):
            with PreserveLoggingContext(ctx):
                if not check_event_content_hash(pdu):
                    # let's try to distinguish between failures because the event was
                    # redacted (which are somewhat expected) vs actual ball-tampering
                    # incidents.
                    #
                    # This is just a heuristic, so we just assume that if the keys are
                    # about the same between the redacted and received events, then the
                    # received event was probably a redacted copy (but we then use our
                    # *actual* redacted copy to be on the safe side.)
                    redacted_event = prune_event(pdu)
                    if set(redacted_event.keys()) == set(pdu.keys()) and set(
                        six.iterkeys(redacted_event.content)
                    ) == set(six.iterkeys(pdu.content)):
                        logger.info(
                            "Event %s seems to have been redacted; using our redacted "
                            "copy",
                            pdu.event_id,
                        )
                    else:
                        logger.warning(
                            "Event %s content has been tampered, redacting",
                            pdu.event_id,
                        )
                    return redacted_event

                if self.spam_checker.check_event_for_spam(pdu):
                    logger.warning(
                        "Event contains spam, redacting %s: %s",
                        pdu.event_id,
                        pdu.get_pdu_json(),
                    )
                    return prune_event(pdu)

                return pdu

        def errback(failure: Failure, pdu: EventBase):
            failure.trap(SynapseError)
            with PreserveLoggingContext(ctx):
                logger.warning(
                    "Signature check failed for %s: %s",
                    pdu.event_id,
                    failure.getErrorMessage(),
                )
            return failure

        for deferred, pdu in zip(deferreds, pdus):
            deferred.addCallbacks(
                callback, errback, callbackArgs=[pdu], errbackArgs=[pdu]
            )

        return deferreds