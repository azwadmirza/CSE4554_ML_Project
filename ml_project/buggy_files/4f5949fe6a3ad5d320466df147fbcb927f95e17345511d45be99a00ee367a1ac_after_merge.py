    def ensure(self):
        """Ensure that virtual environment exists and is in a good state"""
        self.ensure_path()
        self.ensure_interpreter()
        self.ensure_interpreter_version()
        self.ensure_pip()
        self.ensure_key_modules()