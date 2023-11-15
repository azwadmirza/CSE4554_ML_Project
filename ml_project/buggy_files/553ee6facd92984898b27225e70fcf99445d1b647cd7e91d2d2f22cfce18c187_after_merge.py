    def register_with_event_loop(self, hub):
        """Register the async pool with the current event loop."""
        self._result_handler.register_with_event_loop(hub)
        self.handle_result_event = self._result_handler.handle_event
        self._create_timelimit_handlers(hub)
        self._create_process_handlers(hub)
        self._create_write_handlers(hub)

        # Add handler for when a process exits (calls maintain_pool)
        [self._track_child_process(w, hub) for w in self._pool]
        # Handle_result_event is called whenever one of the
        # result queues are readable.
        stale_fds = []
        for fd in self._fileno_to_outq:
            try:
                hub.add_reader(fd, self.handle_result_event, fd)
            except OSError:
                logger.info("Encountered OSError while trying "
                            "to access fd %s ", fd, exc_info=True)
                stale_fds.append(fd)  # take note of stale fd
        for fd in stale_fds:  # Remove now defunct file descriptors
            self._fileno_to_outq.pop(fd, None)

        # Timers include calling maintain_pool at a regular interval
        # to be certain processes are restarted.
        for handler, interval in items(self.timers):
            hub.call_repeatedly(interval, handler)

        hub.on_tick.add(self.on_poll_start)