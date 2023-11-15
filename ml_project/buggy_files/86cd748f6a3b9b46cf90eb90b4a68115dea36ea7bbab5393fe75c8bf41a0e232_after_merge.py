    def on_tracker_error_alert(self, alert):
        # try-except block here is a workaround and has been added to solve
        # https://github.com/Tribler/tribler/issues/5740
        try:
            url = alert.url
        except UnicodeDecodeError as e:
            self._logger.exception(e)
            return

        peers = self.tracker_status[url][0] if url in self.tracker_status else 0
        if alert.msg:
            status = 'Error: ' + alert.msg
        elif alert.status_code > 0:
            status = 'HTTP status code %d' % alert.status_code
        elif alert.status_code == 0:
            status = 'Timeout'
        else:
            status = 'Not working'

        self.tracker_status[url] = [peers, status]