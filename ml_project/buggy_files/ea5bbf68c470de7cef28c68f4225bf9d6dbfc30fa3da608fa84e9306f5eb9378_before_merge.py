    def __init__(self, my_peer, endpoint, network, metadata_store, settings=None, notifier=None):
        super(RemoteQueryCommunity, self).__init__(my_peer, endpoint, network)

        self.notifier = notifier
        self.max_peers = 60

        self.settings = settings or RemoteQueryCommunitySettings()

        self.mds = metadata_store

        # This set contains all the peers that we queried for subscribed channels over time.
        # It is emptied regularly. The purpose of this set is to work as a filter so we never query the same
        # peer twice. If we do, this should happen realy rarely
        # TODO: use Bloom filter here instead. We actually *want* it to be all-false-positives eventually.
        self.queried_subscribed_channels_peers = set()
        self.queried_peers_limit = 1000

        if self.notifier:
            self.notifier.add_observer(NTFY.POPULARITY_COMMUNITY_ADD_UNKNOWN_TORRENT,
                                       self.on_pc_add_unknown_torrent)

        self.add_message_handler(RemoteSelectPayload, self.on_remote_select)
        self.add_message_handler(SelectResponsePayload, self.on_remote_select_response)

        self.request_cache = RequestCache()