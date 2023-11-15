    def enqueue_maybe_ping(self, *contacts, **kwargs):
        delay = kwargs.get('delay', constants.checkRefreshInterval)
        no_op = (defer.succeed(None), lambda: None)
        for contact in contacts:
            if delay and contact not in self._enqueued_contacts:
                self._pending_contacts.setdefault(contact, self._node.clock.seconds() + delay)
            else:
                self._enqueued_contacts.setdefault(contact, no_op)