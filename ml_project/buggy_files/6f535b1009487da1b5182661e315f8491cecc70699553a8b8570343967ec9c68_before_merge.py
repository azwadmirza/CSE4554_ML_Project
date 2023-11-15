    def _pop(self):
        """Pop a question from the queue and ask it, if there are any."""
        log.prompt.debug("Popping from queue {}".format(self._queue))
        if self._queue:
            question = self._queue.popleft()
            if not sip.isdeleted(question):
                # the question could already be deleted, e.g. by a cancelled
                # download. See
                # https://github.com/qutebrowser/qutebrowser/issues/415
                self.ask_question(question, blocking=False)