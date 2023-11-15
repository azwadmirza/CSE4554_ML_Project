    def populate(self):
        self.responses = run_commands(self.module, list(self.COMMANDS), check_rc=False)