    def shutdown(self, *args, **kwargs):
        if not self._shutdown:
            self._shutdown = True