    def __init__(self, session):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._session = session

        self._tracker_id_to_url_dict = {}
        self._tracker_dict = {}

        # if a tracker fails this amount of times in a roll, its 'is_alive' will be marked as 0 (dead).
        self._max_tracker_failures = MAX_TRACKER_FAILURES

        # A "dead" tracker will be retired every this amount of time (in seconds)
        self._tracker_retry_interval = TRACKER_RETRY_INTERVAL