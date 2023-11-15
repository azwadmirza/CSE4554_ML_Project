    def process_alert(self, alert, hops=0):
        alert_type = str(type(alert)).split("'")[1].split(".")[-1]

        # Periodically, libtorrent will send us a state_update_alert, which contains the torrent status of
        # all torrents changed since the last time we received this alert.
        if alert_type == 'state_update_alert':
            for status in alert.status:
                infohash = str(status.info_hash)
                if infohash not in self.torrents:
                    self._logger.debug("Got state_update %s for unknown torrent %s", alert_type, infohash)
                    continue
                self.torrents[infohash][0].update_lt_status(status)

        handle = getattr(alert, 'handle', None)
        if handle and handle.is_valid():
            infohash = str(handle.info_hash())
            if infohash in self.torrents:
                self.torrents[infohash][0].process_alert(alert, alert_type)
            else:
                self._logger.debug("Got %s for unknown torrent %s", alert_type, infohash)

        if alert_type == 'add_torrent_alert':
            infohash = str(handle.info_hash())
            if infohash in self.torrents and not self.torrents[infohash][0].deferred_added.called:
                if alert.error.value():
                    self.torrents[infohash][0].deferred_added.errback(alert.error.message())
                    self._logger.debug("Failed to add torrent (%s)", alert.error.message())
                else:
                    self.torrents[infohash][0].deferred_added.callback(handle)
                    self._logger.debug("Added torrent %s", str(handle.info_hash()))
            else:
                self._logger.debug("Added alert for unknown torrent or Deferred already called")

        elif alert_type == 'torrent_removed_alert':
            infohash = str(alert.info_hash)
            if infohash in self.torrents:
                deferred = self.torrents[infohash][0].deferred_removed
                del self.torrents[infohash]
                deferred.callback(None)
                self._logger.debug("Removed torrent %s", infohash)
            else:
                self._logger.debug("Removed alert for unknown torrent")

        elif alert_type == 'peer_disconnected_alert' and \
                self.tribler_session and self.tribler_session.lm.payout_manager:
            self.tribler_session.lm.payout_manager.do_payout(alert.pid.to_string())

        elif alert_type == 'session_stats_alert':
            queued_disk_jobs = alert.values['disk.queued_disk_jobs']
            queued_write_bytes = alert.values['disk.queued_write_bytes']
            num_write_jobs = alert.values['disk.num_write_jobs']

            if queued_disk_jobs == queued_write_bytes == num_write_jobs == 0:
                self.lt_session_shutdown_ready[hops] = True

            if self.session_stats_callback:
                self.session_stats_callback(alert)

        if self.alert_callback:
            self.alert_callback(alert)