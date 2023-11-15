    def initialize(self):
        self._torrent_db = self.tribler_session.open_dbhandler(NTFY_TORRENTS)
        self._reschedule_tracker_select()
        self.socket_mgr = UdpSocketManager()
        self.create_socket_or_schedule()