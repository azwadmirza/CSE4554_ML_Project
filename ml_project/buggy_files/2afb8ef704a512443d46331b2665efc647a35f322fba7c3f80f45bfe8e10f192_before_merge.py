    def _refreshStoringPeers(self):
        self._protocol._ping_queue.enqueue_maybe_ping(*self._dataStore.getStoringContacts())