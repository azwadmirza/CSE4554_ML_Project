    def interaction(self, frame, traceback):
        self.shell.set_completer_frame(frame)
        OldPdb.interaction(self, frame, traceback)