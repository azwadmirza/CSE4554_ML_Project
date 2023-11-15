    def _load_reporter(self):
        name = self._reporter_name.lower()
        if name in self._reporters:
            self.set_reporter(self._reporters[name]())
        else:
            try:
                reporter_class = self._load_reporter_class()
            except (ImportError, AttributeError):
                raise exceptions.InvalidReporterError(name)
            else:
                self.set_reporter(reporter_class())