    def send_request(self, data, tracker_session):
        self.tracker_sessions[tracker_session.transaction_id] = tracker_session
        self.transport.write(data, (tracker_session.ip_address, tracker_session.port))