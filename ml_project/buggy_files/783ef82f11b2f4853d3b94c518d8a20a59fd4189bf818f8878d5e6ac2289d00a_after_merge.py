        def errback(failure: Failure, pdu: EventBase):
            failure.trap(SynapseError)
            with PreserveLoggingContext(ctx):
                logger.warning(
                    "Signature check failed for %s: %s",
                    pdu.event_id,
                    failure.getErrorMessage(),
                )
            return failure