    def fire(self, *, reverse=False, **kwargs):
        if reverse:
            handlers = reversed(self._handlers)
        else:
            handlers = self._handlers
        for handler in handlers:
            try:
                handler(**kwargs)
            except Exception as e:
                logging.error("Uncaught exception in event handler: %s", e)
                unhandled_greenlet_exception = True