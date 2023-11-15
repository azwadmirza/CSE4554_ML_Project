    def failed(self, msg=None):
        """
        This method handles everything that needs to be done when one step
        in the session has failed and thus no data can be obtained.
        """
        self._is_failed = True
        if self.result_deferred and not self.result_deferred.called:
            result_msg = "HTTP tracker failed for url %s" % self._tracker_url
            if msg:
                result_msg += " (error: %s)" % unicode(msg, errors='replace')
            self.result_deferred.errback(ValueError(result_msg))