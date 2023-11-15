        def lock(self):
            try:
                self._do_lock()
                return
            except LockError:
                time.sleep(DEFAULT_TIMEOUT)

            self._do_lock()