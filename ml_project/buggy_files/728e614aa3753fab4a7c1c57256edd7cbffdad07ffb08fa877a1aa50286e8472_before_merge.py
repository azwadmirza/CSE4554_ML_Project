    def do_server_playback(self, flow):
        """
            This method should be called by child classes in the handle_request
            handler. Returns True if playback has taken place, None if not.
        """
        if self.server_playback:
            rflow = self.server_playback.next_flow(flow)
            if not rflow:
                return None
            response = HTTPResponse.from_state(rflow.response.get_state())
            response.is_replay = True
            if self.refresh_server_playback:
                response.refresh()
            flow.reply(response)
            if self.server_playback.count() == 0:
                self.stop_server_playback()
            return True
        return None