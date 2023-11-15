    def run(self):
        """ Start the primary Qt event loop for the interface """

        res = self.exec_()

        try:
            from classes.logger import log
            self.settings.save()
        except Exception:
            log.error("Couldn't save user settings on exit.", exc_info=1)

        # return exit result
        return res