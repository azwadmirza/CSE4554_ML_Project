    async def _get_rooms_changed(
        self, sync_result_builder: "SyncResultBuilder", ignored_users: Set[str]
    ) -> _RoomChanges:
        """Gets the the changes that have happened since the last sync.
        """
        user_id = sync_result_builder.sync_config.user.to_string()
        since_token = sync_result_builder.since_token
        now_token = sync_result_builder.now_token
        sync_config = sync_result_builder.sync_config

        assert since_token

        # Get a list of membership change events that have happened.
        rooms_changed = await self.store.get_membership_changes_for_user(
            user_id, since_token.room_key, now_token.room_key
        )

        mem_change_events_by_room_id = {}  # type: Dict[str, List[EventBase]]
        for event in rooms_changed:
            mem_change_events_by_room_id.setdefault(event.room_id, []).append(event)

        newly_joined_rooms = []
        newly_left_rooms = []
        room_entries = []
        invited = []
        for room_id, events in mem_change_events_by_room_id.items():
            logger.debug(
                "Membership changes in %s: [%s]",
                room_id,
                ", ".join(("%s (%s)" % (e.event_id, e.membership) for e in events)),
            )

            non_joins = [e for e in events if e.membership != Membership.JOIN]
            has_join = len(non_joins) != len(events)

            # We want to figure out if we joined the room at some point since
            # the last sync (even if we have since left). This is to make sure
            # we do send down the room, and with full state, where necessary

            old_state_ids = None
            if room_id in sync_result_builder.joined_room_ids and non_joins:
                # Always include if the user (re)joined the room, especially
                # important so that device list changes are calculated correctly.
                # If there are non-join member events, but we are still in the room,
                # then the user must have left and joined
                newly_joined_rooms.append(room_id)

                # User is in the room so we don't need to do the invite/leave checks
                continue

            if room_id in sync_result_builder.joined_room_ids or has_join:
                old_state_ids = await self.get_state_at(room_id, since_token)
                old_mem_ev_id = old_state_ids.get((EventTypes.Member, user_id), None)
                old_mem_ev = None
                if old_mem_ev_id:
                    old_mem_ev = await self.store.get_event(
                        old_mem_ev_id, allow_none=True
                    )

                # debug for #4422
                if has_join:
                    prev_membership = None
                    if old_mem_ev:
                        prev_membership = old_mem_ev.membership
                    issue4422_logger.debug(
                        "Previous membership for room %s with join: %s (event %s)",
                        room_id,
                        prev_membership,
                        old_mem_ev_id,
                    )

                if not old_mem_ev or old_mem_ev.membership != Membership.JOIN:
                    newly_joined_rooms.append(room_id)

            # If user is in the room then we don't need to do the invite/leave checks
            if room_id in sync_result_builder.joined_room_ids:
                continue

            if not non_joins:
                continue

            # Check if we have left the room. This can either be because we were
            # joined before *or* that we since joined and then left.
            if events[-1].membership != Membership.JOIN:
                if has_join:
                    newly_left_rooms.append(room_id)
                else:
                    if not old_state_ids:
                        old_state_ids = await self.get_state_at(room_id, since_token)
                        old_mem_ev_id = old_state_ids.get(
                            (EventTypes.Member, user_id), None
                        )
                        old_mem_ev = None
                        if old_mem_ev_id:
                            old_mem_ev = await self.store.get_event(
                                old_mem_ev_id, allow_none=True
                            )
                    if old_mem_ev and old_mem_ev.membership == Membership.JOIN:
                        newly_left_rooms.append(room_id)

            # Only bother if we're still currently invited
            should_invite = non_joins[-1].membership == Membership.INVITE
            if should_invite:
                if event.sender not in ignored_users:
                    room_sync = InvitedSyncResult(room_id, invite=non_joins[-1])
                    if room_sync:
                        invited.append(room_sync)

            # Always include leave/ban events. Just take the last one.
            # TODO: How do we handle ban -> leave in same batch?
            leave_events = [
                e
                for e in non_joins
                if e.membership in (Membership.LEAVE, Membership.BAN)
            ]

            if leave_events:
                leave_event = leave_events[-1]
                leave_position = await self.store.get_position_for_event(
                    leave_event.event_id
                )

                # If the leave event happened before the since token then we
                # bail.
                if since_token and not leave_position.persisted_after(
                    since_token.room_key
                ):
                    continue

                # We can safely convert the position of the leave event into a
                # stream token as it'll only be used in the context of this
                # room. (c.f. the docstring of `to_room_stream_token`).
                leave_token = since_token.copy_and_replace(
                    "room_key", leave_position.to_room_stream_token()
                )

                # If this is an out of band message, like a remote invite
                # rejection, we include it in the recents batch. Otherwise, we
                # let _load_filtered_recents handle fetching the correct
                # batches.
                #
                # This is all screaming out for a refactor, as the logic here is
                # subtle and the moving parts numerous.
                if leave_event.internal_metadata.is_out_of_band_membership():
                    batch_events = [leave_event]  # type: Optional[List[EventBase]]
                else:
                    batch_events = None

                room_entries.append(
                    RoomSyncResultBuilder(
                        room_id=room_id,
                        rtype="archived",
                        events=batch_events,
                        newly_joined=room_id in newly_joined_rooms,
                        full_state=False,
                        since_token=since_token,
                        upto_token=leave_token,
                    )
                )

        timeline_limit = sync_config.filter_collection.timeline_limit()

        # Get all events for rooms we're currently joined to.
        room_to_events = await self.store.get_room_events_stream_for_rooms(
            room_ids=sync_result_builder.joined_room_ids,
            from_key=since_token.room_key,
            to_key=now_token.room_key,
            limit=timeline_limit + 1,
        )

        # We loop through all room ids, even if there are no new events, in case
        # there are non room events that we need to notify about.
        for room_id in sync_result_builder.joined_room_ids:
            room_entry = room_to_events.get(room_id, None)

            newly_joined = room_id in newly_joined_rooms
            if room_entry:
                events, start_key = room_entry

                prev_batch_token = now_token.copy_and_replace("room_key", start_key)

                entry = RoomSyncResultBuilder(
                    room_id=room_id,
                    rtype="joined",
                    events=events,
                    newly_joined=newly_joined,
                    full_state=False,
                    since_token=None if newly_joined else since_token,
                    upto_token=prev_batch_token,
                )
            else:
                entry = RoomSyncResultBuilder(
                    room_id=room_id,
                    rtype="joined",
                    events=[],
                    newly_joined=newly_joined,
                    full_state=False,
                    since_token=since_token,
                    upto_token=since_token,
                )

            if newly_joined:
                # debugging for https://github.com/matrix-org/synapse/issues/4422
                issue4422_logger.debug(
                    "RoomSyncResultBuilder events for newly joined room %s: %r",
                    room_id,
                    entry.events,
                )
            room_entries.append(entry)

        return _RoomChanges(room_entries, invited, newly_joined_rooms, newly_left_rooms)