    def datagramReceived(self, data, _):
        # If the incoming data is valid, find the tracker session and give it the data
        if data and len(data) >= 4:
            transaction_id = struct.unpack_from('!i', data, 4)[0]
            if transaction_id in self.tracker_sessions:
                self.tracker_sessions.pop(transaction_id).handle_response(data)