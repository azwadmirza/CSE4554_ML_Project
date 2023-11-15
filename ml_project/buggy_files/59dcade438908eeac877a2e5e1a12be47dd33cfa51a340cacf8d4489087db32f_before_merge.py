        def run(self):
            self._dirs = self.get_dirs()

            for dirname in self._dirs:
                self._watcher.add_watch(dirname, mask=self.event_mask)

            for event in self._watcher.event_gen():
                if event is None:
                    continue

                filename = event[3]

                self._callback(filename)