        def register(self, fileobj, events, data=None):
            key = super(KqueueSelector, self).register(fileobj, events, data)
            if events & EVENT_READ:
                kevent = select.kevent(key.fd,
                                       select.KQ_FILTER_READ,
                                       select.KQ_EV_ADD)

                _syscall_wrapper(self._wrap_control, False, [kevent], 0, 0)

            if events & EVENT_WRITE:
                kevent = select.kevent(key.fd,
                                       select.KQ_FILTER_WRITE,
                                       select.KQ_EV_ADD)

                _syscall_wrapper(self._wrap_control, False, [kevent], 0, 0)

            return key