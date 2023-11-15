    def __init__(self, session):
        resource.Resource.__init__(self)
        self.session = session
        self.events_requests = []

        self.infohashes_sent = set()
        self.channel_cids_sent = set()

        self.session.add_observer(self.on_search_results_channels, SIGNAL_CHANNEL, [SIGNAL_ON_SEARCH_RESULTS])
        self.session.add_observer(self.on_search_results_torrents, SIGNAL_TORRENT, [SIGNAL_ON_SEARCH_RESULTS])
        self.session.add_observer(self.on_upgrader_started, NTFY_UPGRADER, [NTFY_STARTED])
        self.session.add_observer(self.on_upgrader_finished, NTFY_UPGRADER, [NTFY_FINISHED])
        self.session.add_observer(self.on_upgrader_tick, NTFY_UPGRADER_TICK, [NTFY_STARTED])
        self.session.add_observer(self.on_watch_folder_corrupt_torrent,
                                  NTFY_WATCH_FOLDER_CORRUPT_TORRENT, [NTFY_INSERT])
        self.session.add_observer(self.on_new_version_available, NTFY_NEW_VERSION, [NTFY_INSERT])
        self.session.add_observer(self.on_tribler_started, NTFY_TRIBLER, [NTFY_STARTED])
        self.session.add_observer(self.on_channel_discovered, NTFY_CHANNEL, [NTFY_DISCOVERED])
        self.session.add_observer(self.on_torrent_discovered, NTFY_TORRENT, [NTFY_DISCOVERED])
        self.session.add_observer(self.on_torrent_removed_from_channel, NTFY_TORRENT, [NTFY_DELETE])
        self.session.add_observer(self.on_torrent_finished, NTFY_TORRENT, [NTFY_FINISHED])
        self.session.add_observer(self.on_torrent_error, NTFY_TORRENT, [NTFY_ERROR])
        self.session.add_observer(self.on_market_ask, NTFY_MARKET_ON_ASK, [NTFY_UPDATE])
        self.session.add_observer(self.on_market_bid, NTFY_MARKET_ON_BID, [NTFY_UPDATE])
        self.session.add_observer(self.on_market_ask_timeout, NTFY_MARKET_ON_ASK_TIMEOUT, [NTFY_UPDATE])
        self.session.add_observer(self.on_market_bid_timeout, NTFY_MARKET_ON_BID_TIMEOUT, [NTFY_UPDATE])
        self.session.add_observer(self.on_market_transaction_complete,
                                  NTFY_MARKET_ON_TRANSACTION_COMPLETE, [NTFY_UPDATE])
        self.session.add_observer(self.on_market_payment_received, NTFY_MARKET_ON_PAYMENT_RECEIVED, [NTFY_UPDATE])
        self.session.add_observer(self.on_market_payment_sent, NTFY_MARKET_ON_PAYMENT_SENT, [NTFY_UPDATE])
        self.session.add_observer(self.on_resource_event, SIGNAL_RESOURCE_CHECK, [SIGNAL_LOW_SPACE])
        self.session.add_observer(self.on_credit_minig_error, NTFY_CREDIT_MINING, [NTFY_ERROR])