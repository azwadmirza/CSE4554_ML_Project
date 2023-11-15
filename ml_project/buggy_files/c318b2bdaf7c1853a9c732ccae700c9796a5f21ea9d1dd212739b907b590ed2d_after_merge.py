    def _handle_invite(self, room_id: _RoomID, state: dict) -> None:
        """Handle an invite request.

        Always join a room, even if the partner is not whitelisted. That was
        previously done to prevent a malicious node from inviting and spamming
        the user. However, there are cases where nodes trying to create rooms
        for a channel might race and an invite would be received by one node
        which did not yet whitelist the inviting node, as a result the invite
        would wrongfully be ignored. This change removes the whitelist check.
        To prevent spam, we make sure we ignore presence updates and messages
        from non-whitelisted nodes.
        """
        if self._stop_event.ready():
            return

        if self._starting:
            self.log.debug("Queueing invite", room_id=room_id)
            self._invite_queue.append((room_id, state))
            return

        invite_events = [
            event
            for event in state["events"]
            if event["type"] == "m.room.member"
            and event["content"].get("membership") == "invite"
            and event["state_key"] == self._user_id
        ]

        if not invite_events or not invite_events[0]:
            self.log.debug("Invite: no invite event found", room_id=room_id)
            return  # there should always be one and only one invite membership event for us

        self.log.debug("Got invite", room_id=room_id)

        sender = invite_events[0]["sender"]
        user = self._client.get_user(sender)
        self._displayname_cache.warm_users([user])
        peer_address = validate_userid_signature(user)

        if not peer_address:
            self.log.debug(
                "Got invited to a room by invalid signed user - ignoring",
                room_id=room_id,
                user=user,
            )
            return

        sender_join_events = [
            event
            for event in state["events"]
            if event["type"] == "m.room.member"
            and event["content"].get("membership") == "join"
            and event["state_key"] == sender
        ]

        if not sender_join_events or not sender_join_events[0]:
            self.log.debug("Invite: no sender join event", room_id=room_id)
            return  # there should always be one and only one join membership event for the sender

        join_rules_events = [
            event for event in state["events"] if event["type"] == "m.room.join_rules"
        ]

        # room privacy as seen from the event
        private_room: bool = False
        if join_rules_events:
            join_rules_event = join_rules_events[0]
            private_room = join_rules_event["content"].get("join_rule") == "invite"

        # we join room and _set_room_id_for_address despite room privacy and requirements,
        # _get_room_ids_for_address will take care of returning only matching rooms and
        # _leave_unused_rooms will clear it in the future, if and when needed
        room: Optional[Room] = None
        last_ex: Optional[Exception] = None
        retry_interval = 0.1
        for _ in range(JOIN_RETRIES):
            try:
                room = self._client.join_room(room_id)
            except MatrixRequestError as e:
                last_ex = e
                if self._stop_event.wait(retry_interval):
                    break
                retry_interval = retry_interval * 2
            else:
                break
        else:
            assert last_ex is not None
            raise last_ex  # re-raise if couldn't succeed in retries

        assert room is not None, f"joining room {room} failed"

        if self._is_broadcast_room(room):
            # This shouldn't happen with well behaving nodes but we need to defend against it
            # Since we already are a member of all broadcast rooms, the `join()` above is in
            # effect a no-op
            self.log.warning("Got invite to broadcast room, ignoring", inviting_user=user)
            return

        if not room.listeners:
            room.add_listener(self._handle_message, "m.room.message")

        # room state may not populated yet, so we populate 'invite_only' from event
        room.invite_only = private_room

        self._set_room_id_for_address(address=peer_address, room_id=room_id)

        self.log.debug(
            "Joined from invite",
            room_id=room_id,
            aliases=room.aliases,
            inviting_address=to_checksum_address(peer_address),
        )