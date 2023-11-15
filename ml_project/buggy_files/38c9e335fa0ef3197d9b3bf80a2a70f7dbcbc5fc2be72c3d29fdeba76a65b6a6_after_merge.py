        def logerr(string="", err=None):
            "Simple log helper method"
            logger.log_trace()
            self.msg("%s%s" % (string, "" if err is None else " (%s)" % err))