    def on_process_alive(self, pid):
        """Called when reciving the :const:`WORKER_UP` message.

        Marks the process as ready to receive work.
        """
        try:
            proc = next(w for w in self._pool if w.pid == pid)
        except StopIteration:
            return logger.warning('process with pid=%s already exited', pid)
        assert proc.inqW_fd not in self._fileno_to_inq
        assert proc.inqW_fd not in self._all_inqueues
        self._waiting_to_start.discard(proc)
        self._fileno_to_inq[proc.inqW_fd] = proc
        self._fileno_to_synq[proc.synqW_fd] = proc
        self._all_inqueues.add(proc.inqW_fd)