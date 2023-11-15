    def datagramReceived(self, data, _):
        # Find the tracker session and give it the data
        transaction_id = struct.unpack_from('!i', data, 4)[0]
        if transaction_id in self.tracker_sessions:
            self.tracker_sessions.pop(transaction_id).handle_response(data)