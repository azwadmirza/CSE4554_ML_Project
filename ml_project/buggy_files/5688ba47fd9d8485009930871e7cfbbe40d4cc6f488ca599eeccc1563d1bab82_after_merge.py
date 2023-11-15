    def _handle_pyout(self, msg):
        """ Handle display hook output.
        """
        if not self._hidden and self._is_from_this_session(msg):
            data = msg['content']['data']
            if isinstance(data, basestring):
                # plaintext data from pure Python kernel
                text = data
            else:
                # formatted output from DisplayFormatter (IPython kernel)
                text = data.get('text/plain', '')
            self._append_plain_text(text + '\n')