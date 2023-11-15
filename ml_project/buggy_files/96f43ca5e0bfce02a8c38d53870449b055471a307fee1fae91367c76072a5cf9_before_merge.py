        def select(self, timeout=None):
            if timeout is not None:
                timeout = max(timeout, 0)

            max_events = len(self._fd_to_key) * 2
            ready_fds = {}

            kevent_list = _syscall_wrapper(self._kqueue.control, True,
                                           None, max_events, timeout)

            for kevent in kevent_list:
                fd = kevent.ident
                event_mask = kevent.filter
                events = 0
                if event_mask == select.KQ_FILTER_READ:
                    events |= EVENT_READ
                if event_mask == select.KQ_FILTER_WRITE:
                    events |= EVENT_WRITE

                key = self._key_from_fd(fd)
                if key:
                    if key.fd not in ready_fds:
                        ready_fds[key.fd] = (key, events & key.events)
                    else:
                        old_events = ready_fds[key.fd][1]
                        ready_fds[key.fd] = (key, (events | old_events) & key.events)

            return list(ready_fds.values())