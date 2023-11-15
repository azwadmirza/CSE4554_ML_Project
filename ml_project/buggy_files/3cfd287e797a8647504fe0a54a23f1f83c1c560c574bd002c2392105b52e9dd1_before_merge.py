        def handle_check_result(pdu, deferred):
            try:
                res = yield make_deferred_yieldable(deferred)
            except SynapseError:
                res = None

            if not res:
                # Check local db.
                res = yield self.store.get_event(
                    pdu.event_id, allow_rejected=True, allow_none=True
                )

            if not res and pdu.origin != origin:
                try:
                    res = yield defer.ensureDeferred(
                        self.get_pdu(
                            destinations=[pdu.origin],
                            event_id=pdu.event_id,
                            room_version=room_version,
                            outlier=outlier,
                            timeout=10000,
                        )
                    )
                except SynapseError:
                    pass

            if not res:
                logger.warning(
                    "Failed to find copy of %s with valid signature", pdu.event_id
                )

            return res