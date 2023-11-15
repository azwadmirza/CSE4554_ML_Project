    def _process(self):
        # move contacts that are scheduled to join the queue
        if self._pending_contacts:
            now = self._node.clock.seconds()
            for contact in [contact for contact, schedule in self._pending_contacts.items() if schedule <= now]:
                del self._pending_contacts[contact]
                self._enqueued_contacts.setdefault(contact, (defer.succeed(None), lambda: None))
        # spread pings across 60 seconds to avoid flood and/or false negatives
        step = 60.0/float(len(self._enqueued_contacts)) if self._enqueued_contacts else 0
        for index, (contact, (call, _)) in enumerate(self._enqueued_contacts.items()):
            if call.called and not contact.contact_is_good:
                self._enqueued_contacts[contact] = self._node.reactor_callLater(index*step, self._ping, contact)