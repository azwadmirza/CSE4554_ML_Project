    def run(self):
        """
        Blocking and long running tasks for application startup should be
        called from here.
        """
        venv.ensure_and_create()
        self.finished.emit()  # Always called last.