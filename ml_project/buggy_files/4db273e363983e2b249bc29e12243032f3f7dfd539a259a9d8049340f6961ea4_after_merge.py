    async def send_join(
        self, destinations: Iterable[str], pdu: EventBase, room_version: RoomVersion
    ) -> Dict[str, Any]:
        """Sends a join event to one of a list of homeservers.

        Doing so will cause the remote server to add the event to the graph,
        and send the event out to the rest of the federation.

        Args:
            destinations: Candidate homeservers which are probably
                participating in the room.
            pdu: event to be sent
            room_version: the version of the room (according to the server that
                did the make_join)

        Returns:
            a dict with members ``origin`` (a string
            giving the server the event was sent to, ``state`` (?) and
            ``auth_chain``.

        Raises:
            SynapseError: if the chosen remote server returns a 300/400 code.

            RuntimeError: if no servers were reachable.
        """

        async def send_request(destination) -> Dict[str, Any]:
            content = await self._do_send_join(destination, pdu)

            logger.debug("Got content: %s", content)

            state = [
                event_from_pdu_json(p, room_version, outlier=True)
                for p in content.get("state", [])
            ]

            auth_chain = [
                event_from_pdu_json(p, room_version, outlier=True)
                for p in content.get("auth_chain", [])
            ]

            pdus = {p.event_id: p for p in itertools.chain(state, auth_chain)}

            create_event = None
            for e in state:
                if (e.type, e.state_key) == (EventTypes.Create, ""):
                    create_event = e
                    break

            if create_event is None:
                # If the state doesn't have a create event then the room is
                # invalid, and it would fail auth checks anyway.
                raise SynapseError(400, "No create event in state")

            # the room version should be sane.
            create_room_version = create_event.content.get(
                "room_version", RoomVersions.V1.identifier
            )
            if create_room_version != room_version.identifier:
                # either the server that fulfilled the make_join, or the server that is
                # handling the send_join, is lying.
                raise InvalidResponseError(
                    "Unexpected room version %s in create event"
                    % (create_room_version,)
                )

            valid_pdus = await self._check_sigs_and_hash_and_fetch(
                destination,
                list(pdus.values()),
                outlier=True,
                room_version=room_version.identifier,
            )

            valid_pdus_map = {p.event_id: p for p in valid_pdus}

            # NB: We *need* to copy to ensure that we don't have multiple
            # references being passed on, as that causes... issues.
            signed_state = [
                copy.copy(valid_pdus_map[p.event_id])
                for p in state
                if p.event_id in valid_pdus_map
            ]

            signed_auth = [
                valid_pdus_map[p.event_id]
                for p in auth_chain
                if p.event_id in valid_pdus_map
            ]

            # NB: We *need* to copy to ensure that we don't have multiple
            # references being passed on, as that causes... issues.
            for s in signed_state:
                s.internal_metadata = copy.deepcopy(s.internal_metadata)

            # double-check that the same create event has ended up in the auth chain
            auth_chain_create_events = [
                e.event_id
                for e in signed_auth
                if (e.type, e.state_key) == (EventTypes.Create, "")
            ]
            if auth_chain_create_events != [create_event.event_id]:
                raise InvalidResponseError(
                    "Unexpected create event(s) in auth chain: %s"
                    % (auth_chain_create_events,)
                )

            return {
                "state": signed_state,
                "auth_chain": signed_auth,
                "origin": destination,
            }

        return await self._try_destination_list("send_join", destinations, send_request)