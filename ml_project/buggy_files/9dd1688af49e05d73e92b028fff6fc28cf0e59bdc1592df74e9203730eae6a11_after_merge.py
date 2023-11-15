    def run(self):
        """ Start the primary Qt event loop for the interface """

        res = self.exec_()

        try:
            from classes.logger import log
            self.settings.save()
        except Exception as ex:
            log.error("Couldn't save user settings on exit.\n{}".format(ex))

        # return exit result
        return res