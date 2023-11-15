    def set_state_callback(self, usercallback, getpeerlist=False, delay=0.0):
        """ Called by any thread """
        with self.dllock:
            network_get_state_lambda = lambda: self.network_get_state(usercallback, getpeerlist)
            self.session.lm.threadpool.add_task(network_get_state_lambda, delay)