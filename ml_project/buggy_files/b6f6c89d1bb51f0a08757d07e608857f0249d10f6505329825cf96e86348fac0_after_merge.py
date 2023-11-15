    def on_blob(self, peer, blob):
        """
        Callback for when a MetadataBlob message comes in.

        :param peer: the peer that sent us the blob
        :param blob: payload raw data
        """
        try:
            with db_session:
                try:
                    md_list = self.metadata_store.process_compressed_mdblob(blob.raw_blob)
                except (TransactionIntegrityError, CacheIndexError) as err:
                    self._logger.error("DB transaction error when tried to process payload: %s", str(err))
                    return
        # Unfortunately, we have to catch the exception twice, because Pony can raise them both on the exit from
        # db_session, and on calling the line of code
        except (TransactionIntegrityError, CacheIndexError) as err:
            self._logger.error("DB transaction error when tried to process payload: %s", str(err))
            return

        # Check if the guy who send us this metadata actually has an older version of this md than
        # we do, and queue to send it back.
        with db_session:
            reply_list = [md for md, result in md_list if
                          (md and (md.metadata_type == CHANNEL_TORRENT)) and (result == GOT_NEWER_VERSION)]
            reply_blob = entries_to_chunk(reply_list, maximum_payload_size)[0] if reply_list else None
        if reply_blob:
            self.endpoint.send(peer.address, self.ezr_pack(self.NEWS_PUSH_MESSAGE, RawBlobPayload(reply_blob)))