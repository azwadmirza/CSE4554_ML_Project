    def enqueue_maybe_ping(self, *contacts, **kwargs):
        no_op = (defer.succeed(None), lambda: None)
        for contact in contacts:
            self._enqueued_contacts.setdefault(contact, no_op)