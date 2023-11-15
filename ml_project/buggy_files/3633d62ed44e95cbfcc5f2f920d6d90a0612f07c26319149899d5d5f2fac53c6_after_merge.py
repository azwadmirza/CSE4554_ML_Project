    def interaction(self, frame, traceback):
        self.shell.set_completer_frame(frame)
        while True:
            try:
                OldPdb.interaction(self, frame, traceback)
            except KeyboardInterrupt:
                self.shell.write("\nKeyboardInterrupt\n")
            else:
                break