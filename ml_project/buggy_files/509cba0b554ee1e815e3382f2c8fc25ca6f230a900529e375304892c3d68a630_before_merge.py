    def _process(self):
        if not self._enqueued_contacts:
            return
        # spread pings across 60 seconds to avoid flood and/or false negatives
        step = 60.0/float(len(self._enqueued_contacts))
        for index, (contact, (call, _)) in enumerate(self._enqueued_contacts.items()):
            if call.called and not contact.contact_is_good:
                self._enqueued_contacts[contact] = self._node.reactor_callLater(index*step, self._ping, contact)