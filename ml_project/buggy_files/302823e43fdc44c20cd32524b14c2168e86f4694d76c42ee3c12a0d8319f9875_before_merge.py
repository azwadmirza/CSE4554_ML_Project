    def jsonrpc_blob_announce(self, announce_all=None, blob_hash=None,
                              stream_hash=None, sd_hash=None):
        """
        Announce blobs to the DHT

        Usage:
            blob_announce [-a] [<blob_hash> | --blob_hash=<blob_hash>]
                          [<stream_hash> | --stream_hash=<stream_hash>]
                          [<sd_hash> | --sd_hash=<sd_hash>]

        Options:
            -a                                          : announce all the blobs possessed by user
            <blob_hash>, --blob_hash=<blob_hash>        : announce a blob, specified by blob_hash
            <stream_hash>, --stream_hash=<stream_hash>  : announce all blobs associated with
                                                            stream_hash
            <sd_hash>, --sd_hash=<sd_hash>              : announce all blobs associated with
                                                            sd_hash and the sd_hash itself

        Returns:
            (bool) true if successful
        """
        if announce_all:
            yield self.session.blob_manager.immediate_announce_all_blobs()
        else:
            if blob_hash:
                blob_hashes = [blob_hash]
            elif stream_hash:
                blobs = yield self.get_blobs_for_stream_hash(stream_hash)
                blob_hashes = [blob.blob_hash for blob in blobs if blob.get_is_verified()]
            elif sd_hash:
                blobs = yield self.get_blobs_for_sd_hash(sd_hash)
                blob_hashes = [sd_hash] + [blob.blob_hash for blob in blobs if
                                           blob.get_is_verified()]
            else:
                raise Exception('single argument must be specified')
            yield self.session.blob_manager._immediate_announce(blob_hashes)

        response = yield self._render_response(True)
        defer.returnValue(response)