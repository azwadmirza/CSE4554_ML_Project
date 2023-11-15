    def _get_new_peers(self):
        new_conns_needed = self.max_connections_per_stream - len(self._peer_connections)
        if new_conns_needed < 1:
            defer.returnValue([])
        # we always get the peer from the first request creator
        # must be a type BlobRequester...
        request_creator = self._primary_request_creators[0]
        log.debug("%s Trying to get a new peer to connect to", self._get_log_name())

        # find peers for the head blob if configured to do so
        if self.seek_head_blob_first:
            try:
                peers = yield request_creator.get_new_peers_for_head_blob()
                peers = self.return_shuffled_peers_not_connected_to(peers, new_conns_needed)
            except KeyError:
                log.warning("%s does not have a head blob", self._get_log_name())
                peers = []
        else:
            peers = []

        # we didn't find any new peers on the head blob,
        # we have to look for the first unavailable blob
        if not peers:
            peers = yield request_creator.get_new_peers_for_next_unavailable()
            peers = self.return_shuffled_peers_not_connected_to(peers, new_conns_needed)

        log.debug("%s Got a list of peers to choose from: %s",
                    self._get_log_name(), peers)
        log.debug("%s Current connections: %s",
                    self._get_log_name(), self._peer_connections.keys())
        log.debug("%s List of connection states: %s", self._get_log_name(),
                    [p_c_h.connection.state for p_c_h in self._peer_connections.values()])
        defer.returnValue(peers)