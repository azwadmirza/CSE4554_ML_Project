    def on_unload(self):
        if self._watch:
            self._watch.cancel()

        self._agent = None