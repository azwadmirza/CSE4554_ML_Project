    def process_payload(self, payload):
        """
        This routine decides what to do with a given payload and executes the necessary actions.
        To do so, it looks into the database, compares version numbers, etc.
        It returns a list of tuples each of which contain the corresponding new/old object and the actions
        that were performed on that object.
        :param payload: payload to work on
        :return: a list of tuples of (<metadata or payload>, <action type>)
        """

        if payload.metadata_type == DELETED:
            # We only allow people to delete their own entries, thus PKs must match
            node = self.ChannelNode.get_for_update(signature=payload.delete_signature,
                                                   public_key=payload.public_key)
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
        # Now, when we receive the payload C1:(pk, id1, ih2) or C2:(pk, id2, ih1), we have to
        # replace _both_ entries with a single one, to honor the DB uniqueness constraints.

        if payload.metadata_type not in [CHANNEL_TORRENT, REGULAR_TORRENT]:
            return []

        # Check the payload timestamp<->id_ correctness
        if payload.timestamp < payload.id_:
            return []

        # Check if we already have this payload
        node = self.ChannelNode.get_for_update(signature=payload.signature, public_key=payload.public_key)
        if node:
            return [(node, NO_ACTION)]

        # Check for a node with the same infohash
        result = []
        node = self.TorrentMetadata.get_for_update(public_key=database_blob(payload.public_key),
                                                   infohash=database_blob(payload.infohash))
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
        node = self.TorrentMetadata.get_for_update(public_key=database_blob(payload.public_key), id_=payload.id_)
        if node:
            if node.timestamp < payload.timestamp:
                node.set(**payload.to_dict())
                result.append((node, UPDATED_OUR_VERSION))
            elif node.timestamp > payload.timestamp:
                result.append((node, GOT_NEWER_VERSION))
            # Otherwise, we got the same version locally and do nothing.
            # The situation when something was marked for deletion, and then we got here (i.e. we have the same
            # version) should never happen, because this version should have removed the above mentioned thing earlier
            if result:
                self._logger.warning("Broken DB state!")
            return result

        if payload.metadata_type == REGULAR_TORRENT:
            result.append((self.TorrentMetadata.from_payload(payload), UNKNOWN_TORRENT))
        elif payload.metadata_type == CHANNEL_TORRENT:
            result.append((self.ChannelMetadata.from_payload(payload), UNKNOWN_CHANNEL))
            return result

        return result