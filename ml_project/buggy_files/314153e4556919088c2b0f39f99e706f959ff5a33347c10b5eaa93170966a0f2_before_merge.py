    def _check_for_soft_fail(self, event, state, backfilled):
        """Checks if we should soft fail the event, if so marks the event as
        such.

        Args:
            event (FrozenEvent)
            state (dict|None): The state at the event if we don't have all the
                event's prev events
            backfilled (bool): Whether the event is from backfill

        Returns:
            Deferred
        """
        # For new (non-backfilled and non-outlier) events we check if the event
        # passes auth based on the current state. If it doesn't then we
        # "soft-fail" the event.
        do_soft_fail_check = not backfilled and not event.internal_metadata.is_outlier()
        if do_soft_fail_check:
            extrem_ids = yield self.store.get_latest_event_ids_in_room(
                event.room_id,
            )

            extrem_ids = set(extrem_ids)
            prev_event_ids = set(event.prev_event_ids())

            if extrem_ids == prev_event_ids:
                # If they're the same then the current state is the same as the
                # state at the event, so no point rechecking auth for soft fail.
                do_soft_fail_check = False

        if do_soft_fail_check:
            room_version = yield self.store.get_room_version(event.room_id)

            # Calculate the "current state".
            if state is not None:
                # If we're explicitly given the state then we won't have all the
                # prev events, and so we have a gap in the graph. In this case
                # we want to be a little careful as we might have been down for
                # a while and have an incorrect view of the current state,
                # however we still want to do checks as gaps are easy to
                # maliciously manufacture.
                #
                # So we use a "current state" that is actually a state
                # resolution across the current forward extremities and the
                # given state at the event. This should correctly handle cases
                # like bans, especially with state res v2.

                state_sets = yield self.store.get_state_groups(
                    event.room_id, extrem_ids,
                )
                state_sets = list(state_sets.values())
                state_sets.append(state)
                current_state_ids = yield self.state_handler.resolve_events(
                    room_version, state_sets, event,
                )
                current_state_ids = {
                    k: e.event_id for k, e in iteritems(current_state_ids)
                }
            else:
                current_state_ids = yield self.state_handler.get_current_state_ids(
                    event.room_id, latest_event_ids=extrem_ids,
                )

            # Now check if event pass auth against said current state
            auth_types = auth_types_for_event(event)
            current_state_ids = [
                e for k, e in iteritems(current_state_ids)
                if k in auth_types
            ]

            current_auth_events = yield self.store.get_events(current_state_ids)
            current_auth_events = {
                (e.type, e.state_key): e for e in current_auth_events.values()
            }

            try:
                self.auth.check(room_version, event, auth_events=current_auth_events)
            except AuthError as e:
                logger.warn(
                    "Failed current state auth resolution for %r because %s",
                    event, e,
                )
                event.internal_metadata.soft_failed = True