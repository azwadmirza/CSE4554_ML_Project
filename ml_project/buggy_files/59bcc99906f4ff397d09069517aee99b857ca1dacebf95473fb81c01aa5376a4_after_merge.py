    def stop(self):
        map(None, (cancel() for _, (call, cancel) in self._enqueued_contacts.items() if not call.called))
        return self._node.safe_stop_looping_call(self._process_lc)