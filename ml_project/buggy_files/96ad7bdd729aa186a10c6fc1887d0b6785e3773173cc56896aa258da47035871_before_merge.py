    def run(self):
        """
        Blocking and long running tasks for application startup should be
        called from here.
        """
        venv.ensure()
        self.finished.emit()  # Always called last.