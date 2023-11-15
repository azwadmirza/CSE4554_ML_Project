    def _handle_event_socket_recv(self, raw):
        """
        Callback for events on the event sub socket
        """
        mtag, data = self.event.unpack(raw, self.event.serial)

        # see if we have any futures that need this info:
        for (tag, matcher), futures in six.iteritems(self.tag_map):
            try:
                is_matched = matcher(mtag, tag)
            except Exception:  # pylint: disable=broad-except
                log.error("Failed to run a matcher.", exc_info=True)
                is_matched = False

            if not is_matched:
                continue

            for future in futures:
                if future.done():
                    continue
                future.set_result({"data": data, "tag": mtag})
                self.tag_map[(tag, matcher)].remove(future)
                if future in self.timeout_map:
                    salt.ext.tornado.ioloop.IOLoop.current().remove_timeout(
                        self.timeout_map[future]
                    )
                    del self.timeout_map[future]