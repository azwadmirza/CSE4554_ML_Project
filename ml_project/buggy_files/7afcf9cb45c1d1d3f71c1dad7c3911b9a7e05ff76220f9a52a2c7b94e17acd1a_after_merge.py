    def __init__(self, *args, **kwargs):
        self.metadata_store = kwargs.pop('metadata_store')
        self.torrent_checker = kwargs.pop('torrent_checker', None)

        super(PopularityCommunity, self).__init__(*args, **kwargs)

        self.decode_map[MSG_TORRENTS_HEALTH] = self.on_torrents_health

        self.logger.info('Popularity Community initialized (peer mid %s)', hexlify(self.my_peer.mid))
        self.register_task("publish", self.gossip_torrents_health, interval=PUBLISH_INTERVAL)