    async def clone_existing_room(
        self,
        requester: Requester,
        old_room_id: str,
        new_room_id: str,
        new_room_version: RoomVersion,
        tombstone_event_id: str,
    ) -> None:
        """Populate a new room based on an old room

        Args:
            requester: the user requesting the upgrade
            old_room_id : the id of the room to be replaced
            new_room_id: the id to give the new room (should already have been
                created with _gemerate_room_id())
            new_room_version: the new room version to use
            tombstone_event_id: the ID of the tombstone event in the old room.
        """
        user_id = requester.user.to_string()

        if not await self.spam_checker.user_may_create_room(user_id):
            raise SynapseError(403, "You are not permitted to create rooms")

        creation_content = {
            "room_version": new_room_version.identifier,
            "predecessor": {"room_id": old_room_id, "event_id": tombstone_event_id},
        }  # type: JsonDict

        # Check if old room was non-federatable

        # Get old room's create event
        old_room_create_event = await self.store.get_create_event_for_room(old_room_id)

        # Check if the create event specified a non-federatable room
        if not old_room_create_event.content.get("m.federate", True):
            # If so, mark the new room as non-federatable as well
            creation_content["m.federate"] = False

        initial_state = {}

        # Replicate relevant room events
        types_to_copy = (
            (EventTypes.JoinRules, ""),
            (EventTypes.Name, ""),
            (EventTypes.Topic, ""),
            (EventTypes.RoomHistoryVisibility, ""),
            (EventTypes.GuestAccess, ""),
            (EventTypes.RoomAvatar, ""),
            (EventTypes.RoomEncryption, ""),
            (EventTypes.ServerACL, ""),
            (EventTypes.RelatedGroups, ""),
            (EventTypes.PowerLevels, ""),
        )

        old_room_state_ids = await self.store.get_filtered_current_state_ids(
            old_room_id, StateFilter.from_types(types_to_copy)
        )
        # map from event_id to BaseEvent
        old_room_state_events = await self.store.get_events(old_room_state_ids.values())

        for k, old_event_id in old_room_state_ids.items():
            old_event = old_room_state_events.get(old_event_id)
            if old_event:
                initial_state[k] = old_event.content

        # deep-copy the power-levels event before we start modifying it
        # note that if frozen_dicts are enabled, `power_levels` will be a frozen
        # dict so we can't just copy.deepcopy it.
        initial_state[
            (EventTypes.PowerLevels, "")
        ] = power_levels = copy_power_levels_contents(
            initial_state[(EventTypes.PowerLevels, "")]
        )

        # Resolve the minimum power level required to send any state event
        # We will give the upgrading user this power level temporarily (if necessary) such that
        # they are able to copy all of the state events over, then revert them back to their
        # original power level afterwards in _update_upgraded_room_pls

        # Copy over user power levels now as this will not be possible with >100PL users once
        # the room has been created
        # Calculate the minimum power level needed to clone the room
        event_power_levels = power_levels.get("events", {})
        state_default = power_levels.get("state_default", 50)
        ban = power_levels.get("ban", 50)
        needed_power_level = max(state_default, ban, max(event_power_levels.values()))

        # Get the user's current power level, this matches the logic in get_user_power_level,
        # but without the entire state map.
        user_power_levels = power_levels.setdefault("users", {})
        users_default = power_levels.get("users_default", 0)
        current_power_level = user_power_levels.get(user_id, users_default)
        # Raise the requester's power level in the new room if necessary
        if current_power_level < needed_power_level:
            user_power_levels[user_id] = needed_power_level

        await self._send_events_for_new_room(
            requester,
            new_room_id,
            # we expect to override all the presets with initial_state, so this is
            # somewhat arbitrary.
            preset_config=RoomCreationPreset.PRIVATE_CHAT,
            invite_list=[],
            initial_state=initial_state,
            creation_content=creation_content,
            ratelimit=False,
        )

        # Transfer membership events
        old_room_member_state_ids = await self.store.get_filtered_current_state_ids(
            old_room_id, StateFilter.from_types([(EventTypes.Member, None)])
        )

        # map from event_id to BaseEvent
        old_room_member_state_events = await self.store.get_events(
            old_room_member_state_ids.values()
        )
        for old_event in old_room_member_state_events.values():
            # Only transfer ban events
            if (
                "membership" in old_event.content
                and old_event.content["membership"] == "ban"
            ):
                await self.room_member_handler.update_membership(
                    requester,
                    UserID.from_string(old_event["state_key"]),
                    new_room_id,
                    "ban",
                    ratelimit=False,
                    content=old_event.content,
                )