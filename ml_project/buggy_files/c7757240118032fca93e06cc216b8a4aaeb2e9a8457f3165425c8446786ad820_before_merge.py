    def jsonrpc_blob_list(self, uri=None, stream_hash=None, sd_hash=None, needed=None,
                          finished=None, page_size=None, page=None):
        """
        Returns blob hashes. If not given filters, returns all blobs known by the blob manager

        Usage:
            blob_list [-n] [-f] [<uri> | --uri=<uri>] [<stream_hash> | --stream_hash=<stream_hash>]
                      [<sd_hash> | --sd_hash=<sd_hash>] [<page_size> | --page_size=<page_size>]
                      [<page> | --page=<page>]

        Options:
            -n                                          : only return needed blobs
            -f                                          : only return finished blobs
            <uri>, --uri=<uri>                          : filter blobs by stream in a uri
            <stream_hash>, --stream_hash=<stream_hash>  : filter blobs by stream hash
            <sd_hash>, --sd_hash=<sd_hash>              : filter blobs by sd hash
            <page_size>, --page_size=<page_size>        : results page size
            <page>, --page=<page>                       : page of results to return

        Returns:
            (list) List of blob hashes
        """

        if uri:
            metadata = yield self._resolve_name(uri)
            sd_hash = utils.get_sd_hash(metadata)
            try:
                blobs = yield self.get_blobs_for_sd_hash(sd_hash)
            except NoSuchSDHash:
                blobs = []
        elif stream_hash:
            try:
                blobs = yield self.get_blobs_for_stream_hash(stream_hash)
            except NoSuchStreamHash:
                blobs = []
        elif sd_hash:
            try:
                blobs = yield self.get_blobs_for_sd_hash(sd_hash)
            except NoSuchSDHash:
                blobs = []
        else:
            blobs = self.session.blob_manager.blobs.itervalues()

        if needed:
            blobs = [blob for blob in blobs if not blob.get_is_verified()]
        if finished:
            blobs = [blob for blob in blobs if blob.get_is_verified()]

        blob_hashes = [blob.blob_hash for blob in blobs]
        page_size = page_size or len(blob_hashes)
        page = page or 0
        start_index = page * page_size
        stop_index = start_index + page_size
        blob_hashes_for_return = blob_hashes[start_index:stop_index]
        response = yield self._render_response(blob_hashes_for_return)
        defer.returnValue(response)