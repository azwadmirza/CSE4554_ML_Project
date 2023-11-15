    def _check_sigs_and_hash_and_fetch(
        self, origin, pdus, room_version, outlier=False, include_none=False
    ):
        """Takes a list of PDUs and checks the signatures and hashs of each
        one. If a PDU fails its signature check then we check if we have it in
        the database and if not then request if from the originating server of
        that PDU.

        If a PDU fails its content hash check then it is redacted.

        The given list of PDUs are not modified, instead the function returns
        a new list.

        Args:
            origin (str)
            pdu (list)
            room_version (str)
            outlier (bool): Whether the events are outliers or not
            include_none (str): Whether to include None in the returned list
                for events that have failed their checks

        Returns:
            Deferred : A list of PDUs that have valid signatures and hashes.
        """
        deferreds = self._check_sigs_and_hashes(room_version, pdus)

        @defer.inlineCallbacks
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

        handle = preserve_fn(handle_check_result)
        deferreds2 = [handle(pdu, deferred) for pdu, deferred in zip(pdus, deferreds)]

        valid_pdus = yield make_deferred_yieldable(
            defer.gatherResults(deferreds2, consumeErrors=True)
        ).addErrback(unwrapFirstError)

        if include_none:
            return valid_pdus
        else:
            return [p for p in valid_pdus if p]