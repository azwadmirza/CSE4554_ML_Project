    def remove_if_stale(self):
        """Remove the lock if the process isn't running.

        I.e. process does not respons to signal.
        """
        try:
            pid = self.read_pid()
        except ValueError:
            print('Broken pidfile found - Removing it.', file=sys.stderr)
            self.remove()
            return True
        if not pid:
            self.remove()
            return True

        try:
            os.kill(pid, 0)
        except os.error as exc:
            if exc.errno == errno.ESRCH:
                print('Stale pidfile exists - Removing it.', file=sys.stderr)
                self.remove()
                return True
        except SystemError:
            print('Stale pidfile exists - Removing it.', file=sys.stderr)
            self.remove()
            return True
        return False