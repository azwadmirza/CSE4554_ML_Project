        def callback(_, pdu):
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