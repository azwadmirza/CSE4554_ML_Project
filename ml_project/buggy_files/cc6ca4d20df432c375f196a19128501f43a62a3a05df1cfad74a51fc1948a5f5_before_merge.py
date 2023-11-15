    def on_pc_add_unknown_torrent(self, peer, infohash):
        query = {'infohash': hexlify(infohash)}
        self.send_remote_select(peer, **query)