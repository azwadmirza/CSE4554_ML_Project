        def unregister(self, fileobj):
            key = super(KqueueSelector, self).unregister(fileobj)
            if key.events & EVENT_READ:
                kevent = select.kevent(key.fd,
                                       select.KQ_FILTER_READ,
                                       select.KQ_EV_DELETE)
                try:
                    _syscall_wrapper(self._kqueue.control, False, [kevent], 0, 0)
                except SelectorError:
                    pass
            if key.events & EVENT_WRITE:
                kevent = select.kevent(key.fd,
                                       select.KQ_FILTER_WRITE,
                                       select.KQ_EV_DELETE)
                try:
                    _syscall_wrapper(self._kqueue.control, False, [kevent], 0, 0)
                except SelectorError:
                    pass

            return key