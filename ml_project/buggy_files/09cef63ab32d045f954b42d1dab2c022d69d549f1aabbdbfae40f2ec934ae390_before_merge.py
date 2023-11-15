    def stop_instance(self, fast=False):
        """
        I attempt to stop a running VM.
        I make sure any connection to the worker is removed.
        If the VM was using a cloned image, I remove the clone
        When everything is tidied up, I ask that bbot looks for work to do
        """
        log.msg("Attempting to stop '%s'" % self.workername)
        if self.domain is None:
            log.msg("I don't think that domain is even running, aborting")
            return defer.succeed(None)

        domain = self.domain
        self.domain = None

        if self.graceful_shutdown and not fast:
            log.msg("Graceful shutdown chosen for %s" % self.workername)
            d = domain.shutdown()
        else:
            d = domain.destroy()

        @d.addCallback
        def _disconnect(res):
            log.msg("VM destroyed (%s): Forcing its connection closed." %
                    self.workername)
            return super().disconnect()

        @d.addBoth
        def _disconnected(res):
            log.msg(
                "We forced disconnection (%s), cleaning up and triggering new build" % self.workername)
            if self.base_image:
                os.remove(self.image)
            self.botmaster.maybeStartBuildsForWorker(self.workername)
            return res

        return d