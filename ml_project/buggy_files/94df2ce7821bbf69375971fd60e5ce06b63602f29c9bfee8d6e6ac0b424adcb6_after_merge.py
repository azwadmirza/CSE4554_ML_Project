    async def get_pdu(
        self,
        destinations: Iterable[str],
        event_id: str,
        room_version: RoomVersion,
        outlier: bool = False,
        timeout: Optional[int] = None,
    ) -> Optional[EventBase]:
        """Requests the PDU with given origin and ID from the remote home
        servers.

        Will attempt to get the PDU from each destination in the list until
        one succeeds.

        Args:
            destinations: Which homeservers to query
            event_id: event to fetch
            room_version: version of the room
            outlier: Indicates whether the PDU is an `outlier`, i.e. if
                it's from an arbitary point in the context as opposed to part
                of the current block of PDUs. Defaults to `False`
            timeout: How long to try (in ms) each destination for before
                moving to the next destination. None indicates no timeout.

        Returns:
            The requested PDU, or None if we were unable to find it.
        """

        # TODO: Rate limit the number of times we try and get the same event.

        ev = self._get_pdu_cache.get(event_id)
        if ev:
            return ev

        pdu_attempts = self.pdu_destination_tried.setdefault(event_id, {})

        signed_pdu = None
        for destination in destinations:
            now = self._clock.time_msec()
            last_attempt = pdu_attempts.get(destination, 0)
            if last_attempt + PDU_RETRY_TIME_MS > now:
                continue

            try:
                transaction_data = await self.transport_layer.get_event(
                    destination, event_id, timeout=timeout
                )

                logger.debug(
                    "retrieved event id %s from %s: %r",
                    event_id,
                    destination,
                    transaction_data,
                )

                pdu_list = [
                    event_from_pdu_json(p, room_version, outlier=outlier)
                    for p in transaction_data["pdus"]
                ]  # type: List[EventBase]

                if pdu_list and pdu_list[0]:
                    pdu = pdu_list[0]

                    # Check signatures are correct.
                    signed_pdu = await self._check_sigs_and_hash(
                        room_version.identifier, pdu
                    )

                    break

                pdu_attempts[destination] = now

            except SynapseError as e:
                logger.info(
                    "Failed to get PDU %s from %s because %s", event_id, destination, e
                )
                continue
            except NotRetryingDestination as e:
                logger.info(str(e))
                continue
            except FederationDeniedError as e:
                logger.info(str(e))
                continue
            except Exception as e:
                pdu_attempts[destination] = now

                logger.info(
                    "Failed to get PDU %s from %s because %s", event_id, destination, e
                )
                continue

        if signed_pdu:
            self._get_pdu_cache[event_id] = signed_pdu

        return signed_pdu