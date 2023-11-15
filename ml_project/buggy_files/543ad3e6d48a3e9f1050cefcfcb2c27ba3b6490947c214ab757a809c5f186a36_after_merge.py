    def set_state_callback(self, usercallback, getpeerlist=False):
        """ Called by any thread """
        with self.dllock:
            reactor.callFromThread(lambda: self.network_get_state(usercallback, getpeerlist))