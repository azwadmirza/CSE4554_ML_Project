        def critical_error():
            jlog.error("Failure to get blockheight from Bitcoin Core.")
            self.stopService()
            return False