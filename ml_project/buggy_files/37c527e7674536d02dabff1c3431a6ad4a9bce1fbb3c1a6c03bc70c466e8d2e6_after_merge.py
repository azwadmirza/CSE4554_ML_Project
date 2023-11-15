        def critical_error():
            jlog.error("Critical error updating blockheight.")
            # this cleanup (a) closes the wallet, removing the lock
            # and (b) signals to clients that the service is no longer
            # in a running state, both of which can be useful
            # post reactor shutdown.
            self.stopService()
            stop_reactor()
            return False