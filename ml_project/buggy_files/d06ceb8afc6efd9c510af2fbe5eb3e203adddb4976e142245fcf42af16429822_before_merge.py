    def _get_public_room_list(
        self,
        limit=None,
        since_token=None,
        search_filter=None,
        network_tuple=EMPTY_THIRD_PARTY_ID,
        from_federation=False,
    ):
        """Generate a public room list.
        Args:
            limit (int|None): Maximum amount of rooms to return.
            since_token (str|None)
            search_filter (dict|None): Dictionary to filter rooms by.
            network_tuple (ThirdPartyInstanceID): Which public list to use.
                This can be (None, None) to indicate the main list, or a particular
                appservice and network id to use an appservice specific one.
                Setting to None returns all public rooms across all lists.
            from_federation (bool): Whether this request originated from a
                federating server or a client. Used for room filtering.
        """

        # Pagination tokens work by storing the room ID sent in the last batch,
        # plus the direction (forwards or backwards). Next batch tokens always
        # go forwards, prev batch tokens always go backwards.

        if since_token:
            batch_token = RoomListNextBatch.from_token(since_token)

            bounds = (batch_token.last_joined_members, batch_token.last_room_id)
            forwards = batch_token.direction_is_forward
        else:
            batch_token = None
            bounds = None

            forwards = True

        # we request one more than wanted to see if there are more pages to come
        probing_limit = limit + 1 if limit is not None else None

        results = yield self.store.get_largest_public_rooms(
            network_tuple,
            search_filter,
            probing_limit,
            bounds=bounds,
            forwards=forwards,
            ignore_non_federatable=from_federation,
        )

        def build_room_entry(room):
            entry = {
                "room_id": room["room_id"],
                "name": room["name"],
                "topic": room["topic"],
                "canonical_alias": room["canonical_alias"],
                "num_joined_members": room["joined_members"],
                "avatar_url": room["avatar"],
                "world_readable": room["history_visibility"] == "world_readable",
                "guest_can_join": room["guest_access"] == "can_join",
            }

            # Filter out Nones – rather omit the field altogether
            return {k: v for k, v in entry.items() if v is not None}

        results = [build_room_entry(r) for r in results]

        response = {}
        num_results = len(results)
        if limit is not None:
            more_to_come = num_results == probing_limit

            # Depending on direction we trim either the front or back.
            if forwards:
                results = results[:limit]
            else:
                results = results[-limit:]
        else:
            more_to_come = False

        if num_results > 0:
            final_entry = results[-1]
            initial_entry = results[0]

            if forwards:
                if batch_token:
                    # If there was a token given then we assume that there
                    # must be previous results.
                    response["prev_batch"] = RoomListNextBatch(
                        last_joined_members=initial_entry["num_joined_members"],
                        last_room_id=initial_entry["room_id"],
                        direction_is_forward=False,
                    ).to_token()

                if more_to_come:
                    response["next_batch"] = RoomListNextBatch(
                        last_joined_members=final_entry["num_joined_members"],
                        last_room_id=final_entry["room_id"],
                        direction_is_forward=True,
                    ).to_token()
            else:
                if batch_token:
                    response["next_batch"] = RoomListNextBatch(
                        last_joined_members=final_entry["num_joined_members"],
                        last_room_id=final_entry["room_id"],
                        direction_is_forward=True,
                    ).to_token()

                if more_to_come:
                    response["prev_batch"] = RoomListNextBatch(
                        last_joined_members=initial_entry["num_joined_members"],
                        last_room_id=initial_entry["room_id"],
                        direction_is_forward=False,
                    ).to_token()

        response["chunk"] = results

        response["total_room_count_estimate"] = yield self.store.count_public_rooms(
            network_tuple, ignore_non_federatable=from_federation
        )

        return response