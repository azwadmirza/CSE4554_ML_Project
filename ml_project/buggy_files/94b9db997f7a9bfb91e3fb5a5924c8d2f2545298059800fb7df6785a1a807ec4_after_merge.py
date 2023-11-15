    def _populate_stats_process_rooms(self, progress, batch_size):

        if not self.stats_enabled:
            yield self._end_background_update("populate_stats_process_rooms")
            defer.returnValue(1)

        # If we don't have progress filed, delete everything.
        if not progress:
            yield self.delete_all_stats()

        def _get_next_batch(txn):
            # Only fetch 250 rooms, so we don't fetch too many at once, even
            # if those 250 rooms have less than batch_size state events.
            sql = """
                SELECT room_id, events FROM %s_rooms
                ORDER BY events DESC
                LIMIT 250
            """ % (
                TEMP_TABLE,
            )
            txn.execute(sql)
            rooms_to_work_on = txn.fetchall()

            if not rooms_to_work_on:
                return None

            # Get how many are left to process, so we can give status on how
            # far we are in processing
            txn.execute("SELECT COUNT(*) FROM " + TEMP_TABLE + "_rooms")
            progress["remaining"] = txn.fetchone()[0]

            return rooms_to_work_on

        rooms_to_work_on = yield self.runInteraction(
            "populate_stats_temp_read", _get_next_batch
        )

        # No more rooms -- complete the transaction.
        if not rooms_to_work_on:
            yield self._end_background_update("populate_stats_process_rooms")
            defer.returnValue(1)

        logger.info(
            "Processing the next %d rooms of %d remaining",
            len(rooms_to_work_on), progress["remaining"],
        )

        # Number of state events we've processed by going through each room
        processed_event_count = 0

        for room_id, event_count in rooms_to_work_on:

            current_state_ids = yield self.get_current_state_ids(room_id)

            join_rules = yield self.get_event(
                current_state_ids.get((EventTypes.JoinRules, "")), allow_none=True
            )
            history_visibility = yield self.get_event(
                current_state_ids.get((EventTypes.RoomHistoryVisibility, "")),
                allow_none=True,
            )
            encryption = yield self.get_event(
                current_state_ids.get((EventTypes.RoomEncryption, "")), allow_none=True
            )
            name = yield self.get_event(
                current_state_ids.get((EventTypes.Name, "")), allow_none=True
            )
            topic = yield self.get_event(
                current_state_ids.get((EventTypes.Topic, "")), allow_none=True
            )
            avatar = yield self.get_event(
                current_state_ids.get((EventTypes.RoomAvatar, "")), allow_none=True
            )
            canonical_alias = yield self.get_event(
                current_state_ids.get((EventTypes.CanonicalAlias, "")), allow_none=True
            )

            def _or_none(x, arg):
                if x:
                    return x.content.get(arg)
                return None

            yield self.update_room_state(
                room_id,
                {
                    "join_rules": _or_none(join_rules, "join_rule"),
                    "history_visibility": _or_none(
                        history_visibility, "history_visibility"
                    ),
                    "encryption": _or_none(encryption, "algorithm"),
                    "name": _or_none(name, "name"),
                    "topic": _or_none(topic, "topic"),
                    "avatar": _or_none(avatar, "url"),
                    "canonical_alias": _or_none(canonical_alias, "alias"),
                },
            )

            now = self.hs.get_reactor().seconds()

            # quantise time to the nearest bucket
            now = (now // self.stats_bucket_size) * self.stats_bucket_size

            def _fetch_data(txn):

                # Get the current token of the room
                current_token = self._get_max_stream_id_in_current_state_deltas_txn(txn)

                current_state_events = len(current_state_ids)
                joined_members = self._get_user_count_in_room_txn(
                    txn, room_id, Membership.JOIN
                )
                invited_members = self._get_user_count_in_room_txn(
                    txn, room_id, Membership.INVITE
                )
                left_members = self._get_user_count_in_room_txn(
                    txn, room_id, Membership.LEAVE
                )
                banned_members = self._get_user_count_in_room_txn(
                    txn, room_id, Membership.BAN
                )
                total_state_events = self._get_total_state_event_counts_txn(
                    txn, room_id
                )

                self._update_stats_txn(
                    txn,
                    "room",
                    room_id,
                    now,
                    {
                        "bucket_size": self.stats_bucket_size,
                        "current_state_events": current_state_events,
                        "joined_members": joined_members,
                        "invited_members": invited_members,
                        "left_members": left_members,
                        "banned_members": banned_members,
                        "state_events": total_state_events,
                    },
                )
                self._simple_insert_txn(
                    txn,
                    "room_stats_earliest_token",
                    {"room_id": room_id, "token": current_token},
                )

            yield self.runInteraction("update_room_stats", _fetch_data)

            # We've finished a room. Delete it from the table.
            yield self._simple_delete_one(TEMP_TABLE + "_rooms", {"room_id": room_id})
            # Update the remaining counter.
            progress["remaining"] -= 1
            yield self.runInteraction(
                "populate_stats",
                self._background_update_progress_txn,
                "populate_stats_process_rooms",
                progress,
            )

            processed_event_count += event_count

            if processed_event_count > batch_size:
                # Don't process any more rooms, we've hit our batch size.
                defer.returnValue(processed_event_count)

        defer.returnValue(processed_event_count)