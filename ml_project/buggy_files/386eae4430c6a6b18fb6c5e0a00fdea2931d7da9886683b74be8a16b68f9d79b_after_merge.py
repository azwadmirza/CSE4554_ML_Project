    def process_payload(self, payload, skip_personal_metadata_payload=True):
        """
        This routine decides what to do with a given payload and executes the necessary actions.
        To do so, it looks into the database, compares version numbers, etc.
        It returns a list of tuples each of which contain the corresponding new/old object and the actions
        that were performed on that object.
        :param payload: payload to work on
        :param skip_personal_metadata_payload: if this is set to True, personal torrent metadata payload received
                through gossip will be ignored. The default value is True.
        :return: a list of tuples of (<metadata or payload>, <action type>)
        """

        if payload.metadata_type == DELETED:
            # We only allow people to delete their own entries, thus PKs must match
            node = self.ChannelNode.get_for_update(signature=payload.delete_signature, public_key=payload.public_key)
            if node:
                node.delete()
                return [(None, DELETED_METADATA)]

        # Check if we already got an older version of the same node that we can update, and
        # check the uniqueness constraint on public_key+infohash tuple. If the received entry
        # has the same tuple as the entry we already have, update our entry if necessary.
        # This procedure is necessary to handle the case when the original author of the payload
        # had created another entry with the same infohash earlier, deleted it, and sent
        # the different versions to two different peers.
        # There is a corner case where there already exist 2 entries in our database that match both
        # update conditions:
        # A: (pk, id1, ih1)
        # B: (pk, id2, ih2)
        # When we receive the payload C1:(pk, id1, ih2) or C2:(pk, id2, ih1), we have to
        # replace _both_ entries with a single one, to honor the DB uniqueness constraints.

        if payload.metadata_type not in [CHANNEL_TORRENT, REGULAR_TORRENT, COLLECTION_NODE]:
            return []

        # Check for offending words stop-list
        if is_forbidden(payload.title + payload.tags):
            return [(None, NO_ACTION)]

        # FFA payloads get special treatment:
        if payload.public_key == NULL_KEY:
            if payload.metadata_type == REGULAR_TORRENT:
                node = self.TorrentMetadata.add_ffa_from_dict(payload.to_dict())
                if node:
                    return [(node, UNKNOWN_TORRENT)]
            return [(None, NO_ACTION)]

        # Check if we already have this payload
        node = self.ChannelNode.get(signature=payload.signature, public_key=payload.public_key)
        if node:
            return [(node, NO_ACTION)]

        result = []
        if payload.metadata_type in [CHANNEL_TORRENT, REGULAR_TORRENT]:
            # Signed entry > FFA entry. Old FFA entry > new FFA entry
            ffa_node = self.TorrentMetadata.get(public_key=database_blob(b""), infohash=database_blob(payload.infohash))
            if ffa_node:
                ffa_node.delete()

            def check_update_opportunity():
                # Check for possible update sending opportunity.
                node = self.TorrentMetadata.get(
                    lambda g: g.public_key == database_blob(payload.public_key)
                    and g.id_ == payload.id_
                    and g.timestamp > payload.timestamp
                )
                return [(node, GOT_NEWER_VERSION)] if node else [(None, NO_ACTION)]

            # Check if the received payload is a deleted entry from a channel that we already have
            parent_channel = self.ChannelMetadata.get(
                public_key=database_blob(payload.public_key), id_=payload.origin_id
            )
            if parent_channel and parent_channel.local_version > payload.timestamp:
                return check_update_opportunity()

            # If we received a metadata payload signed by ourselves we simply ignore it since we are the only
            # authoritative source of information about our own channel.
            if skip_personal_metadata_payload and payload.public_key == bytes(
                database_blob(self.my_key.pub().key_to_bin()[10:])
            ):
                return check_update_opportunity()

            # Check for a node with the same infohash
            node = self.TorrentMetadata.get_for_update(
                public_key=database_blob(payload.public_key), infohash=database_blob(payload.infohash)
            )
            if node:
                if node.timestamp < payload.timestamp:
                    node.delete()
                    result.append((None, DELETED_METADATA))
                elif node.timestamp > payload.timestamp:
                    result.append((node, GOT_NEWER_VERSION))
                    return result
                else:
                    return result
                # Otherwise, we got the same version locally and do nothing.

        # Check for the older version of the same node
        node = self.ChannelNode.get_for_update(public_key=database_blob(payload.public_key), id_=payload.id_)
        if node:
            if node.timestamp < payload.timestamp:
                # Workaround for a corner case of remote change of md type.
                # We delete the original node and replace it with the updated one
                if node.metadata_type != payload.metadata_type:
                    if payload.metadata_type == REGULAR_TORRENT:
                        node.delete()
                        renewed_node = self.TorrentMetadata.from_payload(payload)
                    elif payload.metadata_type == CHANNEL_TORRENT:
                        node.delete()
                        renewed_node = self.ChannelMetadata.from_payload(payload)
                    elif payload.metadata_type == COLLECTION_NODE:
                        node.delete()
                        renewed_node = self.CollectionNode.from_payload(payload)
                    else:
                        self._logger.warning(
                            f"Tried to update channel node to illegal type: "
                            f" original type: {node.metadata_type}"
                            f" updated type: {payload.metadata_type}"
                            f" {hexlify(payload.public_key)}, {payload.id_} "
                        )
                        return result
                    result.append((renewed_node, UPDATED_OUR_VERSION))
                    return result
                else:
                    node.set(**payload.to_dict())
                    result.append((node, UPDATED_OUR_VERSION))
                    return result
            elif node.timestamp > payload.timestamp:
                result.append((node, GOT_NEWER_VERSION))
                return result
            # Otherwise, we got the same version locally and do nothing.
            # The situation when something was marked for deletion, and then we got here (i.e. we have the same or
            # newer version) should never happen, because this version should have removed the node we deleted earlier
            if result:
                self._logger.warning("Broken DB state!")
            return result

        if payload.metadata_type == REGULAR_TORRENT:
            result.append((self.TorrentMetadata.from_payload(payload), UNKNOWN_TORRENT))
        elif payload.metadata_type == CHANNEL_TORRENT:
            result.append((self.ChannelMetadata.from_payload(payload), UNKNOWN_CHANNEL))
        elif payload.metadata_type == COLLECTION_NODE:
            result.append((self.CollectionNode.from_payload(payload), UNKNOWN_COLLECTION))
        return result