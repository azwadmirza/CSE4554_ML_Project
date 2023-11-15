    def stop(self):
        """Stop creating the stream. Create the terminating zero-length blob."""
        log.debug("stop has been called for StreamCreator")
        self.stopped = True
        if self.current_blob is not None:
            self._close_current_blob()
        self._finalize()
        dl = defer.DeferredList(self.finished_deferreds)
        dl.addCallback(lambda _: self._finished())
        dl.addErrback(self._error)
        return dl