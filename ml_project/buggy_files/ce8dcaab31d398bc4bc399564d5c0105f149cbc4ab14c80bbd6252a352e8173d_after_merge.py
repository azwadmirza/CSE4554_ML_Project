    def _handle_state_delta(self, deltas):
        """Process current state deltas to find new joins that need to be
        handled.
        """
        for delta in deltas:
            typ = delta["type"]
            state_key = delta["state_key"]
            room_id = delta["room_id"]
            event_id = delta["event_id"]
            prev_event_id = delta["prev_event_id"]

            logger.debug("Handling: %r %r, %s", typ, state_key, event_id)

            if typ != EventTypes.Member:
                continue

            if event_id is None:
                # state has been deleted, so this is not a join. We only care about
                # joins.
                continue

            event = yield self.store.get_event(event_id)
            if event.content.get("membership") != Membership.JOIN:
                # We only care about joins
                continue

            if prev_event_id:
                prev_event = yield self.store.get_event(prev_event_id)
                if prev_event.content.get("membership") == Membership.JOIN:
                    # Ignore changes to join events.
                    continue

            yield self._on_user_joined_room(room_id, state_key)