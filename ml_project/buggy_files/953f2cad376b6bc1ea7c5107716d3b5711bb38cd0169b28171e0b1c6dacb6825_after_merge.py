    def _handle_message(self, room: Room, event: Dict[str, Any]) -> bool:
        """ Handle text messages sent to listening rooms """
        if self._stop_event.ready():
            return False

        is_valid_type = (
            event["type"] == "m.room.message" and event["content"]["msgtype"] == "m.text"
        )
        if not is_valid_type:
            return False

        sender_id = event["sender"]

        if sender_id == self._user_id:
            # Ignore our own messages
            return False

        user = self._client.get_user(sender_id)
        self._displayname_cache.warm_users([user])

        peer_address = validate_userid_signature(user)
        if not peer_address:
            self.log.debug(
                "Ignoring message from user with an invalid display name signature",
                peer_user=user.user_id,
                room=room,
            )
            return False

        if self._is_broadcast_room(room):
            # This must not happen. Nodes must not listen on broadcast rooms.
            raise RuntimeError(
                f"Received message in broadcast room {room.aliases[0]}. Sending user: {user}"
            )

        if not self._address_mgr.is_address_known(peer_address):
            self.log.debug(
                "Ignoring message from non-whitelisted peer",
                sender=user,
                sender_address=to_checksum_address(peer_address),
                room=room,
            )
            return False

        # rooms we created and invited user, or were invited specifically by them
        room_ids = self._get_room_ids_for_address(peer_address)

        if room.room_id not in room_ids:
            self.log.debug(
                "Ignoring invalid message",
                peer_user=user.user_id,
                peer_address=to_checksum_address(peer_address),
                room=room,
                expected_room_ids=room_ids,
                reason="unknown room for user",
            )
            return False

        messages = validate_and_parse_message(event["content"]["body"], peer_address)

        if not messages:
            return False

        self.log.debug(
            "Incoming messages",
            messages=messages,
            sender=to_checksum_address(peer_address),
            sender_user=user,
            room=room,
        )

        for message in messages:
            if not isinstance(message, (SignedRetrieableMessage, SignedMessage)):
                self.log.warning(
                    "Received invalid message",
                    message=redact_secret(DictSerializer.serialize(message)),
                )
            if isinstance(message, Delivered):
                self._receive_delivered(message)
            elif isinstance(message, Processed):
                self._receive_message(message)
            else:
                assert isinstance(message, SignedRetrieableMessage)
                self._receive_message(message)

        return True