    async def backfill(
        self, dest: str, room_id: str, limit: int, extremities: Iterable[str]
    ) -> List[EventBase]:
        """Requests some more historic PDUs for the given room from the
        given destination server.

        Args:
            dest (str): The remote homeserver to ask.
            room_id (str): The room_id to backfill.
            limit (int): The maximum number of events to return.
            extremities (list): our current backwards extremities, to backfill from
        """
        logger.debug("backfill extrem=%s", extremities)

        # If there are no extremeties then we've (probably) reached the start.
        if not extremities:
            return

        transaction_data = await self.transport_layer.backfill(
            dest, room_id, extremities, limit
        )

        logger.debug("backfill transaction_data=%r", transaction_data)

        room_version = await self.store.get_room_version(room_id)

        pdus = [
            event_from_pdu_json(p, room_version, outlier=False)
            for p in transaction_data["pdus"]
        ]

        # FIXME: We should handle signature failures more gracefully.
        pdus[:] = await make_deferred_yieldable(
            defer.gatherResults(
                self._check_sigs_and_hashes(room_version.identifier, pdus),
                consumeErrors=True,
            ).addErrback(unwrapFirstError)
        )

        return pdus