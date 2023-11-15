    def failed(self, msg=None):
        """
        This method handles everything that needs to be done when one step
        in the session has failed and thus no data can be obtained.
        """
        if self.result_deferred and not self.result_deferred.called and not self._is_failed:
            result_msg = "UDP tracker failed for url %s" % self._tracker_url
            if msg:
                result_msg += " (error: %s)" % text_type(msg, errors='replace')
            self.result_deferred.errback(ValueError(result_msg))

        self._is_failed = True