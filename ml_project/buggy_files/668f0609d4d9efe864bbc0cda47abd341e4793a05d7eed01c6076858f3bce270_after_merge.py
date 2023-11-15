    async def _generate_room_entry(
        self,
        sync_result_builder: "SyncResultBuilder",
        ignored_users: FrozenSet[str],
        room_builder: "RoomSyncResultBuilder",
        ephemeral: List[JsonDict],
        tags: Optional[Dict[str, Dict[str, Any]]],
        account_data: Dict[str, JsonDict],
        always_include: bool = False,
    ):
        """Populates the `joined` and `archived` section of `sync_result_builder`
        based on the `room_builder`.

        Args:
            sync_result_builder
            ignored_users: Set of users ignored by user.
            room_builder
            ephemeral: List of new ephemeral events for room
            tags: List of *all* tags for room, or None if there has been
                no change.
            account_data: List of new account data for room
            always_include: Always include this room in the sync response,
                even if empty.
        """
        newly_joined = room_builder.newly_joined
        full_state = (
            room_builder.full_state or newly_joined or sync_result_builder.full_state
        )
        events = room_builder.events

        # We want to shortcut out as early as possible.
        if not (always_include or account_data or ephemeral or full_state):
            if events == [] and tags is None:
                return

        now_token = sync_result_builder.now_token
        sync_config = sync_result_builder.sync_config

        room_id = room_builder.room_id
        since_token = room_builder.since_token
        upto_token = room_builder.upto_token

        batch = await self._load_filtered_recents(
            room_id,
            sync_config,
            now_token=upto_token,
            since_token=since_token,
            potential_recents=events,
            newly_joined_room=newly_joined,
        )

        # Note: `batch` can be both empty and limited here in the case where
        # `_load_filtered_recents` can't find any events the user should see
        # (e.g. due to having ignored the sender of the last 50 events).

        if newly_joined:
            # debug for https://github.com/matrix-org/synapse/issues/4422
            issue4422_logger.debug(
                "Timeline events after filtering in newly-joined room %s: %r",
                room_id,
                batch,
            )

        # When we join the room (or the client requests full_state), we should
        # send down any existing tags. Usually the user won't have tags in a
        # newly joined room, unless either a) they've joined before or b) the
        # tag was added by synapse e.g. for server notice rooms.
        if full_state:
            user_id = sync_result_builder.sync_config.user.to_string()
            tags = await self.store.get_tags_for_room(user_id, room_id)

            # If there aren't any tags, don't send the empty tags list down
            # sync
            if not tags:
                tags = None

        account_data_events = []
        if tags is not None:
            account_data_events.append({"type": "m.tag", "content": {"tags": tags}})

        for account_data_type, content in account_data.items():
            account_data_events.append({"type": account_data_type, "content": content})

        account_data_events = sync_config.filter_collection.filter_room_account_data(
            account_data_events
        )

        ephemeral = sync_config.filter_collection.filter_room_ephemeral(ephemeral)

        if not (
            always_include or batch or account_data_events or ephemeral or full_state
        ):
            return

        state = await self.compute_state_delta(
            room_id, batch, sync_config, since_token, now_token, full_state=full_state
        )

        summary = {}  # type: Optional[JsonDict]

        # we include a summary in room responses when we're lazy loading
        # members (as the client otherwise doesn't have enough info to form
        # the name itself).
        if sync_config.filter_collection.lazy_load_members() and (
            # we recalulate the summary:
            #   if there are membership changes in the timeline, or
            #   if membership has changed during a gappy sync, or
            #   if this is an initial sync.
            any(ev.type == EventTypes.Member for ev in batch.events)
            or (
                # XXX: this may include false positives in the form of LL
                # members which have snuck into state
                batch.limited
                and any(t == EventTypes.Member for (t, k) in state)
            )
            or since_token is None
        ):
            summary = await self.compute_summary(
                room_id, sync_config, batch, state, now_token
            )

        if room_builder.rtype == "joined":
            unread_notifications = {}  # type: Dict[str, int]
            room_sync = JoinedSyncResult(
                room_id=room_id,
                timeline=batch,
                state=state,
                ephemeral=ephemeral,
                account_data=account_data_events,
                unread_notifications=unread_notifications,
                summary=summary,
                unread_count=0,
            )

            if room_sync or always_include:
                notifs = await self.unread_notifs_for_room_id(room_id, sync_config)

                unread_notifications["notification_count"] = notifs["notify_count"]
                unread_notifications["highlight_count"] = notifs["highlight_count"]

                room_sync.unread_count = notifs["unread_count"]

                sync_result_builder.joined.append(room_sync)

            if batch.limited and since_token:
                user_id = sync_result_builder.sync_config.user.to_string()
                logger.debug(
                    "Incremental gappy sync of %s for user %s with %d state events"
                    % (room_id, user_id, len(state))
                )
        elif room_builder.rtype == "archived":
            archived_room_sync = ArchivedSyncResult(
                room_id=room_id,
                timeline=batch,
                state=state,
                account_data=account_data_events,
            )
            if archived_room_sync or always_include:
                sync_result_builder.archived.append(archived_room_sync)
        else:
            raise Exception("Unrecognized rtype: %r", room_builder.rtype)