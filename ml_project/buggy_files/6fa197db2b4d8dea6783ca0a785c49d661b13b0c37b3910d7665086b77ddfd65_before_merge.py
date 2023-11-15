    def ask(self, mtype, m):
        """
            Decorate a message with a reply attribute, and send it to the
            master.  then wait for a response.
        """
        m.reply = Reply(m)
        self.q.put((mtype, m))
        while not self.should_exit.is_set():
            try:
                # The timeout is here so we can handle a should_exit event.
                g = m.reply.q.get(timeout=0.5)
            except queue.Empty:  # pragma: no cover
                continue
            return g