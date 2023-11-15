async def filter_events_for_client(
    storage: Storage,
    user_id,
    events,
    is_peeking=False,
    always_include_ids=frozenset(),
    filter_send_to_client=True,
):
    """
    Check which events a user is allowed to see. If the user can see the event but its
    sender asked for their data to be erased, prune the content of the event.

    Args:
        storage
        user_id(str): user id to be checked
        events(list[synapse.events.EventBase]): sequence of events to be checked
        is_peeking(bool): should be True if:
          * the user is not currently a member of the room, and:
          * the user has not been a member of the room since the given
            events
        always_include_ids (set(event_id)): set of event ids to specifically
            include (unless sender is ignored)
        filter_send_to_client (bool): Whether we're checking an event that's going to be
            sent to a client. This might not always be the case since this function can
            also be called to check whether a user can see the state at a given point.

    Returns:
        list[synapse.events.EventBase]
    """
    # Filter out events that have been soft failed so that we don't relay them
    # to clients.
    events = [e for e in events if not e.internal_metadata.is_soft_failed()]

    types = ((EventTypes.RoomHistoryVisibility, ""), (EventTypes.Member, user_id))
    event_id_to_state = await storage.state.get_state_for_events(
        frozenset(e.event_id for e in events),
        state_filter=StateFilter.from_types(types),
    )

    ignore_dict_content = await storage.main.get_global_account_data_by_type_for_user(
        "m.ignored_user_list", user_id
    )

    # FIXME: This will explode if people upload something incorrect.
    ignore_list = frozenset(
        ignore_dict_content.get("ignored_users", {}).keys()
        if ignore_dict_content
        else []
    )

    erased_senders = await storage.main.are_users_erased((e.sender for e in events))

    if filter_send_to_client:
        room_ids = {e.room_id for e in events}
        retention_policies = {}

        for room_id in room_ids:
            retention_policies[
                room_id
            ] = await storage.main.get_retention_policy_for_room(room_id)

    def allowed(event):
        """
        Args:
            event (synapse.events.EventBase): event to check

        Returns:
            None|EventBase:
               None if the user cannot see this event at all

               a redacted copy of the event if they can only see a redacted
               version

               the original event if they can see it as normal.
        """
        # Only run some checks if these events aren't about to be sent to clients. This is
        # because, if this is not the case, we're probably only checking if the users can
        # see events in the room at that point in the DAG, and that shouldn't be decided
        # on those checks.
        if filter_send_to_client:
            if event.type == "org.matrix.dummy_event":
                return None

            if not event.is_state() and event.sender in ignore_list:
                return None

            # Until MSC2261 has landed we can't redact malicious alias events, so for
            # now we temporarily filter out m.room.aliases entirely to mitigate
            # abuse, while we spec a better solution to advertising aliases
            # on rooms.
            if event.type == EventTypes.Aliases:
                return None

            # Don't try to apply the room's retention policy if the event is a state
            # event, as MSC1763 states that retention is only considered for non-state
            # events.
            if not event.is_state():
                retention_policy = retention_policies[event.room_id]
                max_lifetime = retention_policy.get("max_lifetime")

                if max_lifetime is not None:
                    oldest_allowed_ts = storage.main.clock.time_msec() - max_lifetime

                    if event.origin_server_ts < oldest_allowed_ts:
                        return None

        if event.event_id in always_include_ids:
            return event

        state = event_id_to_state[event.event_id]

        # get the room_visibility at the time of the event.
        visibility_event = state.get((EventTypes.RoomHistoryVisibility, ""), None)
        if visibility_event:
            visibility = visibility_event.content.get("history_visibility", "shared")
        else:
            visibility = "shared"

        if visibility not in VISIBILITY_PRIORITY:
            visibility = "shared"

        # Always allow history visibility events on boundaries. This is done
        # by setting the effective visibility to the least restrictive
        # of the old vs new.
        if event.type == EventTypes.RoomHistoryVisibility:
            prev_content = event.unsigned.get("prev_content", {})
            prev_visibility = prev_content.get("history_visibility", None)

            if prev_visibility not in VISIBILITY_PRIORITY:
                prev_visibility = "shared"

            new_priority = VISIBILITY_PRIORITY.index(visibility)
            old_priority = VISIBILITY_PRIORITY.index(prev_visibility)
            if old_priority < new_priority:
                visibility = prev_visibility

        # likewise, if the event is the user's own membership event, use
        # the 'most joined' membership
        membership = None
        if event.type == EventTypes.Member and event.state_key == user_id:
            membership = event.content.get("membership", None)
            if membership not in MEMBERSHIP_PRIORITY:
                membership = "leave"

            prev_content = event.unsigned.get("prev_content", {})
            prev_membership = prev_content.get("membership", None)
            if prev_membership not in MEMBERSHIP_PRIORITY:
                prev_membership = "leave"

            # Always allow the user to see their own leave events, otherwise
            # they won't see the room disappear if they reject the invite
            if membership == "leave" and (
                prev_membership == "join" or prev_membership == "invite"
            ):
                return event

            new_priority = MEMBERSHIP_PRIORITY.index(membership)
            old_priority = MEMBERSHIP_PRIORITY.index(prev_membership)
            if old_priority < new_priority:
                membership = prev_membership

        # otherwise, get the user's membership at the time of the event.
        if membership is None:
            membership_event = state.get((EventTypes.Member, user_id), None)
            if membership_event:
                membership = membership_event.membership

        # if the user was a member of the room at the time of the event,
        # they can see it.
        if membership == Membership.JOIN:
            return event

        # otherwise, it depends on the room visibility.

        if visibility == "joined":
            # we weren't a member at the time of the event, so we can't
            # see this event.
            return None

        elif visibility == "invited":
            # user can also see the event if they were *invited* at the time
            # of the event.
            return event if membership == Membership.INVITE else None

        elif visibility == "shared" and is_peeking:
            # if the visibility is shared, users cannot see the event unless
            # they have *subequently* joined the room (or were members at the
            # time, of course)
            #
            # XXX: if the user has subsequently joined and then left again,
            # ideally we would share history up to the point they left. But
            # we don't know when they left. We just treat it as though they
            # never joined, and restrict access.
            return None

        # the visibility is either shared or world_readable, and the user was
        # not a member at the time. We allow it, provided the original sender
        # has not requested their data to be erased, in which case, we return
        # a redacted version.
        if erased_senders[event.sender]:
            return prune_event(event)

        return event

    # check each event: gives an iterable[None|EventBase]
    filtered_events = map(allowed, events)

    # remove the None entries
    filtered_events = filter(operator.truth, filtered_events)

    # we turn it into a list before returning it.
    return list(filtered_events)