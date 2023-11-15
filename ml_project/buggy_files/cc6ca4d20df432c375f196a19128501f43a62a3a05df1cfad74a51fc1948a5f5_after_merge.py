    def on_pc_add_unknown_torrent(self, peer, infohash):
        if not self.enable_resolve_unknown_torrents_feature:
            return
        query = {'infohash': hexlify(infohash)}
        self.send_remote_select(peer, **query)