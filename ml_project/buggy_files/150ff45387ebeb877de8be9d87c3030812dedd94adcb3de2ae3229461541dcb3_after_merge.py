    def on_disconnect_trigger(self, mc):
        """Mark the specified message channel as
        disconnected. Track loss of private connections
        to individual nicks. If no message channels are
        now connected, fire on_disconnect to calling code.
        """
        self.mc_status[mc] = 2
        self.flush_nicks()
        # construct a readable nicks seen:
        readablens = dict([(k.hostid, self.nicks_seen[k]) for k in self.nicks_seen])
        log.debug("On disconnect fired, nicks_seen is now: " + str(
            readablens) + " " + mc.hostid)
        if not any([x == 1 for x in self.mc_status.values()]):
            if self.on_disconnect:
                self.on_disconnect()