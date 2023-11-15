    def actionJumpStart_trigger(self, checked=True):
        log.info("actionJumpStart_trigger")

        # Seek to the 1st frame
        self.SeekSignal.emit(1)