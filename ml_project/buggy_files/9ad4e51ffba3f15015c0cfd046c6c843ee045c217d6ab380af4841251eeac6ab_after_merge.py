    async def _generate_sync_entry_for_rooms(
        self,
        sync_result_builder: "SyncResultBuilder",
        account_data_by_room: Dict[str, Dict[str, JsonDict]],
    ) -> Tuple[Set[str], Set[str], Set[str], Set[str]]:
        """Generates the rooms portion of the sync response. Populates the
        `sync_result_builder` with the result.

        Args:
            sync_result_builder
            account_data_by_room: Dictionary of per room account data

        Returns:
            Returns a 4-tuple of
            `(newly_joined_rooms, newly_joined_or_invited_users,
            newly_left_rooms, newly_left_users)`
        """
        user_id = sync_result_builder.sync_config.user.to_string()
        block_all_room_ephemeral = (
            sync_result_builder.since_token is None
            and sync_result_builder.sync_config.filter_collection.blocks_all_room_ephemeral()
        )

        if block_all_room_ephemeral:
            ephemeral_by_room = {}  # type: Dict[str, List[JsonDict]]
        else:
            now_token, ephemeral_by_room = await self.ephemeral_by_room(
                sync_result_builder,
                now_token=sync_result_builder.now_token,
                since_token=sync_result_builder.since_token,
            )
            sync_result_builder.now_token = now_token

        # We check up front if anything has changed, if it hasn't then there is
        # no point in going further.
        since_token = sync_result_builder.since_token
        if not sync_result_builder.full_state:
            if since_token and not ephemeral_by_room and not account_data_by_room:
                have_changed = await self._have_rooms_changed(sync_result_builder)
                if not have_changed:
                    tags_by_room = await self.store.get_updated_tags(
                        user_id, since_token.account_data_key
                    )
                    if not tags_by_room:
                        logger.debug("no-oping sync")
                        return set(), set(), set(), set()

        ignored_account_data = await self.store.get_global_account_data_by_type_for_user(
            AccountDataTypes.IGNORED_USER_LIST, user_id=user_id
        )

        # If there is ignored users account data and it matches the proper type,
        # then use it.
        ignored_users = frozenset()  # type: FrozenSet[str]
        if ignored_account_data:
            ignored_users_data = ignored_account_data.get("ignored_users", {})
            if isinstance(ignored_users_data, dict):
                ignored_users = frozenset(ignored_users_data.keys())

        if since_token:
            room_changes = await self._get_rooms_changed(
                sync_result_builder, ignored_users
            )
            tags_by_room = await self.store.get_updated_tags(
                user_id, since_token.account_data_key
            )
        else:
            room_changes = await self._get_all_rooms(sync_result_builder, ignored_users)

            tags_by_room = await self.store.get_tags_for_user(user_id)

        room_entries = room_changes.room_entries
        invited = room_changes.invited
        newly_joined_rooms = room_changes.newly_joined_rooms
        newly_left_rooms = room_changes.newly_left_rooms

        async def handle_room_entries(room_entry):
            logger.debug("Generating room entry for %s", room_entry.room_id)
            res = await self._generate_room_entry(
                sync_result_builder,
                ignored_users,
                room_entry,
                ephemeral=ephemeral_by_room.get(room_entry.room_id, []),
                tags=tags_by_room.get(room_entry.room_id),
                account_data=account_data_by_room.get(room_entry.room_id, {}),
                always_include=sync_result_builder.full_state,
            )
            logger.debug("Generated room entry for %s", room_entry.room_id)
            return res

        await concurrently_execute(handle_room_entries, room_entries, 10)

        sync_result_builder.invited.extend(invited)

        # Now we want to get any newly joined or invited users
        newly_joined_or_invited_users = set()
        newly_left_users = set()
        if since_token:
            for joined_sync in sync_result_builder.joined:
                it = itertools.chain(
                    joined_sync.timeline.events, joined_sync.state.values()
                )
                for event in it:
                    if event.type == EventTypes.Member:
                        if (
                            event.membership == Membership.JOIN
                            or event.membership == Membership.INVITE
                        ):
                            newly_joined_or_invited_users.add(event.state_key)
                        else:
                            prev_content = event.unsigned.get("prev_content", {})
                            prev_membership = prev_content.get("membership", None)
                            if prev_membership == Membership.JOIN:
                                newly_left_users.add(event.state_key)

        newly_left_users -= newly_joined_or_invited_users

        return (
            set(newly_joined_rooms),
            newly_joined_or_invited_users,
            set(newly_left_rooms),
            newly_left_users,
        )