    def __init__(self, session, channel_community, rss_url, check_interval=DEFAULT_CHECK_INTERVAL):
        super(ChannelRssParser, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)

        self.session = session
        self.channel_community = channel_community
        self.rss_url = rss_url
        self.check_interval = check_interval

        self._url_cache = None

        self._pending_metadata_requests = {}

        self._to_stop = False

        self.running = False