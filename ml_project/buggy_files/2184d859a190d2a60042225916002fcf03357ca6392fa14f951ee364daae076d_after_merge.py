        def select(self, timeout=None):
            # Selecting on empty lists on Windows errors out.
            if not len(self._readers) and not len(self._writers):
                return []

            timeout = None if timeout is None else max(timeout, 0.0)
            ready = []
            r, w, _ = _syscall_wrapper(self._select, True, self._readers,
                                       self._writers, timeout=timeout)
            r = set(r)
            w = set(w)
            for fd in r | w:
                events = 0
                if fd in r:
                    events |= EVENT_READ
                if fd in w:
                    events |= EVENT_WRITE

                key = self._key_from_fd(fd)
                if key:
                    ready.append((key, events & key.events))
            return ready