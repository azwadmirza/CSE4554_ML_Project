    def _maybe_create_room_for_address(self, address: Address) -> None:
        if self._stop_event.ready():
            return None

        if self._get_room_for_address(address):
            return None

        assert self._raiden_service is not None, "_raiden_service not set"

        # The rooms creation is asymmetric, only the node with the lower
        # address is responsible to create the room. This fixes race conditions
        # were the two nodes try to create a room with each other at the same
        # time, leading to communications problems if the nodes choose a
        # different room.
        #
        # This does not introduce a new attack vector, since not creating the
        # room is the same as being unresponsive.
        room_creator_address = my_place_or_yours(
            our_address=self._raiden_service.address, partner_address=address
        )
        if self._raiden_service.address != room_creator_address:
            self.log.debug(
                "This node should not create the room",
                partner_address=to_checksum_address(address),
            )
            return None

        with self.room_creation_lock[address]:
            candidates = self._client.search_user_directory(to_normalized_address(address))
            self._displayname_cache.warm_users(candidates)

            partner_users = [
                user for user in candidates if validate_userid_signature(user) == address
            ]
            partner_user_ids = [user.user_id for user in partner_users]

            if not partner_users:
                self.log.error(
                    "Partner doesn't have a user", partner_address=to_checksum_address(address)
                )

                return None

            room = self._client.create_room(None, invitees=partner_user_ids, is_public=False)
            self.log.debug("Created private room", room=room, invitees=partner_users)

            self.log.debug(
                "Fetching room members", room=room, partner_address=to_checksum_address(address)
            )

            def partner_joined(fetched_members: List[User]) -> bool:
                if fetched_members is None:
                    return False
                return any(member.user_id in partner_user_ids for member in fetched_members)

            members = self.retry_api_call(
                room.get_joined_members, verify_response=partner_joined, force_resync=True
            )

            assert members is not None, "fetching members failed"

            if not partner_joined(members):
                self.log.debug(
                    "Peer has not joined from invite yet, should join eventually",
                    room=room,
                    partner_address=to_checksum_address(address),
                    retry_interval=RETRY_INTERVAL,
                )

            # Here, the list of valid user ids is composed of
            # all known partner user ids along with our own.
            # If our partner roams, the user will be invited to
            # the room, resulting in multiple user ids for the partner.
            # If we roam, a new user and room will be created and only
            # the new user shall be in the room.
            valid_user_ids = partner_user_ids + [self._client.user_id]
            has_unexpected_user_ids = any(
                member.user_id not in valid_user_ids for member in members
            )

            if has_unexpected_user_ids:
                self._leave_unexpected_rooms([room], "Private room has unexpected participants")
                return None

            self._address_mgr.add_userids_for_address(
                address, {user.user_id for user in partner_users}
            )

            self._set_room_id_for_address(address, room.room_id)

            self.log.debug("Channel room", peer_address=to_checksum_address(address), room=room)
            return room