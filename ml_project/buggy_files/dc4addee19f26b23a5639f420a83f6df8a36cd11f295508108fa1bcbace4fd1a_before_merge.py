    async def _get_all_rooms(
        self, sync_result_builder: "SyncResultBuilder", ignored_users: Set[str]
    ) -> _RoomChanges:
        """Returns entries for all rooms for the user.

        Args:
            sync_result_builder
            ignored_users: Set of users ignored by user.

        """

        user_id = sync_result_builder.sync_config.user.to_string()
        since_token = sync_result_builder.since_token
        now_token = sync_result_builder.now_token
        sync_config = sync_result_builder.sync_config

        membership_list = (
            Membership.INVITE,
            Membership.JOIN,
            Membership.LEAVE,
            Membership.BAN,
        )

        room_list = await self.store.get_rooms_for_local_user_where_membership_is(
            user_id=user_id, membership_list=membership_list
        )

        room_entries = []
        invited = []

        for event in room_list:
            if event.membership == Membership.JOIN:
                room_entries.append(
                    RoomSyncResultBuilder(
                        room_id=event.room_id,
                        rtype="joined",
                        events=None,
                        newly_joined=False,
                        full_state=True,
                        since_token=since_token,
                        upto_token=now_token,
                    )
                )
            elif event.membership == Membership.INVITE:
                if event.sender in ignored_users:
                    continue
                invite = await self.store.get_event(event.event_id)
                invited.append(InvitedSyncResult(room_id=event.room_id, invite=invite))
            elif event.membership in (Membership.LEAVE, Membership.BAN):
                # Always send down rooms we were banned or kicked from.
                if not sync_config.filter_collection.include_leave:
                    if event.membership == Membership.LEAVE:
                        if user_id == event.sender:
                            continue

                leave_token = now_token.copy_and_replace(
                    "room_key", RoomStreamToken(None, event.stream_ordering)
                )
                room_entries.append(
                    RoomSyncResultBuilder(
                        room_id=event.room_id,
                        rtype="archived",
                        events=None,
                        newly_joined=False,
                        full_state=True,
                        since_token=since_token,
                        upto_token=leave_token,
                    )
                )

        return _RoomChanges(room_entries, invited, [], [])