    def stop_instance(self, fast=False):
        """
        I attempt to stop a running VM.
        I make sure any connection to the worker is removed.
        If the VM was using a cloned image, I remove the clone
        When everything is tidied up, I ask that bbot looks for work to do
        """
        @defer.inlineCallbacks
        def _destroy_domain(res, domain):
            log.msg('Graceful shutdown failed. Force destroying domain %s' %
                    self.workername)
            # Don't return res to stop propagating shutdown error if destroy
            # was successful.
            yield domain.destroy()

        log.msg("Attempting to stop '%s'" % self.workername)
        if self.domain is None:
            log.msg("I don't think that domain is even running, aborting")
            return defer.succeed(None)

        domain = self.domain
        self.domain = None

        if self.graceful_shutdown and not fast:
            log.msg("Graceful shutdown chosen for %s" % self.workername)
            d = domain.shutdown()
            d.addErrback(_destroy_domain, domain)
        else:
            d = domain.destroy()

        if self.base_image:
            @d.addBoth
            def _remove_image(res):
                log.msg('Removing base image %s for %s' % (self.image,
                                                           self.workername))
                os.remove(self.image)
                return res

        return d