    def compute_state_delta(
        self, room_id, batch, sync_config, since_token, now_token, full_state
    ):
        """ Works out the difference in state between the start of the timeline
        and the previous sync.

        Args:
            room_id(str):
            batch(synapse.handlers.sync.TimelineBatch): The timeline batch for
                the room that will be sent to the user.
            sync_config(synapse.handlers.sync.SyncConfig):
            since_token(str|None): Token of the end of the previous batch. May
                be None.
            now_token(str): Token of the end of the current batch.
            full_state(bool): Whether to force returning the full state.

        Returns:
             A deferred dict of (type, state_key) -> Event
        """
        # TODO(mjark) Check if the state events were received by the server
        # after the previous sync, since we need to include those state
        # updates even if they occured logically before the previous event.
        # TODO(mjark) Check for new redactions in the state events.

        with Measure(self.clock, "compute_state_delta"):

            members_to_fetch = None

            lazy_load_members = sync_config.filter_collection.lazy_load_members()
            include_redundant_members = (
                sync_config.filter_collection.include_redundant_members()
            )

            if lazy_load_members:
                # We only request state for the members needed to display the
                # timeline:

                members_to_fetch = set(
                    event.sender  # FIXME: we also care about invite targets etc.
                    for event in batch.events
                )

                if full_state:
                    # always make sure we LL ourselves so we know we're in the room
                    # (if we are) to fix https://github.com/vector-im/riot-web/issues/7209
                    # We only need apply this on full state syncs given we disabled
                    # LL for incr syncs in #3840.
                    members_to_fetch.add(sync_config.user.to_string())

                state_filter = StateFilter.from_lazy_load_member_list(members_to_fetch)
            else:
                state_filter = StateFilter.all()

            timeline_state = {
                (event.type, event.state_key): event.event_id
                for event in batch.events
                if event.is_state()
            }

            if full_state:
                if batch:
                    current_state_ids = yield self.store.get_state_ids_for_event(
                        batch.events[-1].event_id, state_filter=state_filter
                    )

                    state_ids = yield self.store.get_state_ids_for_event(
                        batch.events[0].event_id, state_filter=state_filter
                    )

                else:
                    current_state_ids = yield self.get_state_at(
                        room_id, stream_position=now_token, state_filter=state_filter
                    )

                    state_ids = current_state_ids

                state_ids = _calculate_state(
                    timeline_contains=timeline_state,
                    timeline_start=state_ids,
                    previous={},
                    current=current_state_ids,
                    lazy_load_members=lazy_load_members,
                )
            elif batch.limited:
                if batch:
                    state_at_timeline_start = yield self.store.get_state_ids_for_event(
                        batch.events[0].event_id, state_filter=state_filter
                    )
                else:
                    # We can get here if the user has ignored the senders of all
                    # the recent events.
                    state_at_timeline_start = yield self.get_state_at(
                        room_id, stream_position=now_token, state_filter=state_filter
                    )

                # for now, we disable LL for gappy syncs - see
                # https://github.com/vector-im/riot-web/issues/7211#issuecomment-419976346
                # N.B. this slows down incr syncs as we are now processing way
                # more state in the server than if we were LLing.
                #
                # We still have to filter timeline_start to LL entries (above) in order
                # for _calculate_state's LL logic to work, as we have to include LL
                # members for timeline senders in case they weren't loaded in the initial
                # sync.  We do this by (counterintuitively) by filtering timeline_start
                # members to just be ones which were timeline senders, which then ensures
                # all of the rest get included in the state block (if we need to know
                # about them).
                state_filter = StateFilter.all()

                state_at_previous_sync = yield self.get_state_at(
                    room_id, stream_position=since_token, state_filter=state_filter
                )

                if batch:
                    current_state_ids = yield self.store.get_state_ids_for_event(
                        batch.events[-1].event_id, state_filter=state_filter
                    )
                else:
                    # Its not clear how we get here, but empirically we do
                    # (#5407). Logging has been added elsewhere to try and
                    # figure out where this state comes from.
                    current_state_ids = yield self.get_state_at(
                        room_id, stream_position=now_token, state_filter=state_filter
                    )

                state_ids = _calculate_state(
                    timeline_contains=timeline_state,
                    timeline_start=state_at_timeline_start,
                    previous=state_at_previous_sync,
                    current=current_state_ids,
                    # we have to include LL members in case LL initial sync missed them
                    lazy_load_members=lazy_load_members,
                )
            else:
                state_ids = {}
                if lazy_load_members:
                    if members_to_fetch and batch.events:
                        # We're returning an incremental sync, with no
                        # "gap" since the previous sync, so normally there would be
                        # no state to return.
                        # But we're lazy-loading, so the client might need some more
                        # member events to understand the events in this timeline.
                        # So we fish out all the member events corresponding to the
                        # timeline here, and then dedupe any redundant ones below.

                        state_ids = yield self.store.get_state_ids_for_event(
                            batch.events[0].event_id,
                            # we only want members!
                            state_filter=StateFilter.from_types(
                                (EventTypes.Member, member)
                                for member in members_to_fetch
                            ),
                        )

            if lazy_load_members and not include_redundant_members:
                cache_key = (sync_config.user.to_string(), sync_config.device_id)
                cache = self.get_lazy_loaded_members_cache(cache_key)

                # if it's a new sync sequence, then assume the client has had
                # amnesia and doesn't want any recent lazy-loaded members
                # de-duplicated.
                if since_token is None:
                    logger.debug("clearing LruCache for %r", cache_key)
                    cache.clear()
                else:
                    # only send members which aren't in our LruCache (either
                    # because they're new to this client or have been pushed out
                    # of the cache)
                    logger.debug("filtering state from %r...", state_ids)
                    state_ids = {
                        t: event_id
                        for t, event_id in iteritems(state_ids)
                        if cache.get(t[1]) != event_id
                    }
                    logger.debug("...to %r", state_ids)

                # add any member IDs we are about to send into our LruCache
                for t, event_id in itertools.chain(
                    state_ids.items(), timeline_state.items()
                ):
                    if t[0] == EventTypes.Member:
                        cache.set(t[1], event_id)

        state = {}
        if state_ids:
            state = yield self.store.get_events(list(state_ids.values()))

        return {
            (e.type, e.state_key): e
            for e in sync_config.filter_collection.filter_room_state(
                list(state.values())
            )
        }