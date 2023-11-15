    def send_request(self, data, tracker_session):
        self.tracker_sessions[tracker_session.transaction_id] = tracker_session
        try:
            self.transport.write(data, (tracker_session.ip_address, tracker_session.port))
        except socket.error as exc:
            self._logger.warning("Unable to write data to %s:%d - %s",
                                 tracker_session.ip_address, tracker_session.port, exc)