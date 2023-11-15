    def _refreshContacts(self):
        self._protocol._ping_queue.enqueue_maybe_ping(*self.contacts, delay=0)