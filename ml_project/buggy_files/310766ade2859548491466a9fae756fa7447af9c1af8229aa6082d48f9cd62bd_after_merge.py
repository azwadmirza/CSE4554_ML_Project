    def upload_room_keys(self, user_id, version, room_keys):
        """Bulk upload a list of room keys into a given backup version, asserting
        that the given version is the current backup version.  room_keys are merged
        into the current backup as described in RoomKeysServlet.on_PUT().

        Args:
            user_id(str): the user whose backup we're setting
            version(str): the version ID of the backup we're updating
            room_keys(dict): a nested dict describing the room_keys we're setting:

        {
            "rooms": {
                "!abc:matrix.org": {
                    "sessions": {
                        "c0ff33": {
                            "first_message_index": 1,
                            "forwarded_count": 1,
                            "is_verified": false,
                            "session_data": "SSBBTSBBIEZJU0gK"
                        }
                    }
                }
            }
        }

        Returns:
            A dict containing the count and etag for the backup version

        Raises:
            NotFoundError: if there are no versions defined
            RoomKeysVersionError: if the uploaded version is not the current version
        """

        # TODO: Validate the JSON to make sure it has the right keys.

        # XXX: perhaps we should use a finer grained lock here?
        with (yield self._upload_linearizer.queue(user_id)):

            # Check that the version we're trying to upload is the current version
            try:
                version_info = yield self.store.get_e2e_room_keys_version_info(user_id)
            except StoreError as e:
                if e.code == 404:
                    raise NotFoundError("Version '%s' not found" % (version,))
                else:
                    raise

            if version_info["version"] != version:
                # Check that the version we're trying to upload actually exists
                try:
                    version_info = yield self.store.get_e2e_room_keys_version_info(
                        user_id, version
                    )
                    # if we get this far, the version must exist
                    raise RoomKeysVersionError(current_version=version_info["version"])
                except StoreError as e:
                    if e.code == 404:
                        raise NotFoundError("Version '%s' not found" % (version,))
                    else:
                        raise

            # Fetch any existing room keys for the sessions that have been
            # submitted.  Then compare them with the submitted keys.  If the
            # key is new, insert it; if the key should be updated, then update
            # it; otherwise, drop it.
            existing_keys = yield self.store.get_e2e_room_keys_multi(
                user_id, version, room_keys["rooms"]
            )
            to_insert = []  # batch the inserts together
            changed = False  # if anything has changed, we need to update the etag
            for room_id, room in iteritems(room_keys["rooms"]):
                for session_id, room_key in iteritems(room["sessions"]):
                    if not isinstance(room_key["is_verified"], bool):
                        msg = (
                            "is_verified must be a boolean in keys for session %s in"
                            "room %s" % (session_id, room_id)
                        )
                        raise SynapseError(400, msg, Codes.INVALID_PARAM)

                    log_kv(
                        {
                            "message": "Trying to upload room key",
                            "room_id": room_id,
                            "session_id": session_id,
                            "user_id": user_id,
                        }
                    )
                    current_room_key = existing_keys.get(room_id, {}).get(session_id)
                    if current_room_key:
                        if self._should_replace_room_key(current_room_key, room_key):
                            log_kv({"message": "Replacing room key."})
                            # updates are done one at a time in the DB, so send
                            # updates right away rather than batching them up,
                            # like we do with the inserts
                            yield self.store.update_e2e_room_key(
                                user_id, version, room_id, session_id, room_key
                            )
                            changed = True
                        else:
                            log_kv({"message": "Not replacing room_key."})
                    else:
                        log_kv(
                            {
                                "message": "Room key not found.",
                                "room_id": room_id,
                                "user_id": user_id,
                            }
                        )
                        log_kv({"message": "Replacing room key."})
                        to_insert.append((room_id, session_id, room_key))
                        changed = True

            if len(to_insert):
                yield self.store.add_e2e_room_keys(user_id, version, to_insert)

            version_etag = version_info["etag"]
            if changed:
                version_etag = version_etag + 1
                yield self.store.update_e2e_room_keys_version(
                    user_id, version, None, version_etag
                )

            count = yield self.store.count_e2e_room_keys(user_id, version)
            return {"etag": str(version_etag), "count": count}