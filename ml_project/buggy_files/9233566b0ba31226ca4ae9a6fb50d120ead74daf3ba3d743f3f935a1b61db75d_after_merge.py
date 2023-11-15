    def _process_queue(self):
        def init_buffer():
            buffer = gzip.GzipFile(fileobj=compat.BytesIO(), mode="w", compresslevel=self._compress_level)
            data = (self._json_serializer({"metadata": self._metadata}) + "\n").encode("utf-8")
            buffer.write(data)
            return buffer

        buffer = init_buffer()
        buffer_written = False
        # add some randomness to timeout to avoid stampedes of several workers that are booted at the same time
        max_flush_time = self._max_flush_time * random.uniform(0.9, 1.1) if self._max_flush_time else None

        while True:
            since_last_flush = timeit.default_timer() - self._last_flush
            # take max flush time into account to calculate timeout
            timeout = max(0, max_flush_time - since_last_flush) if max_flush_time else None
            timed_out = False
            try:
                event_type, data, flush = self._event_queue.get(block=True, timeout=timeout)
            except compat.queue.Empty:
                event_type, data, flush = None, None, None
                timed_out = True

            if event_type == "close":
                if buffer_written:
                    self._flush(buffer)
                self._flushed.set()
                return  # time to go home!

            if data is not None:
                buffer.write((self._json_serializer({event_type: data}) + "\n").encode("utf-8"))
                buffer_written = True
                self._counts[event_type] += 1

            queue_size = 0 if buffer.fileobj is None else buffer.fileobj.tell()

            if flush:
                logger.debug("forced flush")
            elif timed_out or timeout == 0:
                # update last flush time, as we might have waited for a non trivial amount of time in
                # _event_queue.get()
                since_last_flush = timeit.default_timer() - self._last_flush
                logger.debug(
                    "flushing due to time since last flush %.3fs > max_flush_time %.3fs",
                    since_last_flush,
                    max_flush_time,
                )
                flush = True
            elif self._max_buffer_size and queue_size > self._max_buffer_size:
                logger.debug(
                    "flushing since queue size %d bytes > max_queue_size %d bytes", queue_size, self._max_buffer_size
                )
                flush = True
            if flush:
                if buffer_written:
                    self._flush(buffer)
                self._last_flush = timeit.default_timer()
                buffer = init_buffer()
                buffer_written = False
                max_flush_time = self._max_flush_time * random.uniform(0.9, 1.1) if self._max_flush_time else None
                self._flushed.set()