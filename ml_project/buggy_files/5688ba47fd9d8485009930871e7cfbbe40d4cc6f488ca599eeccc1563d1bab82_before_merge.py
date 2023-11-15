    def _handle_pyout(self, msg):
        """ Handle display hook output.
        """
        if not self._hidden and self._is_from_this_session(msg):
            self._append_plain_text(msg['content']['data']['text/plain'] + '\n')