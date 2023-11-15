    def flush_nicks(self):
        """Any message channel which is not
        active must wipe any state information on peers
        connected for that message channel. If a peer is
        available on another chan, switch the active_channel
        for that nick to (an)(the) other, to make failure
        to communicate as unlikely as possible.
        """
        for mc in self.unavailable_channels():
            self.nicks_seen[mc] = set()
            ac = self.active_channels
            for peer in [x for x in ac if ac[x] == mc]:
                for mc2 in self.available_channels():
                    if peer in self.nicks_seen[mc2]:
                        log.debug("Dynamically switching: " + peer + " to: " + \
                                  str(mc2.serverport))
                        self.active_channels[peer] = mc2
                        break
            #Remove all entries for the newly unavailable channel
            self.active_channels = dict([(a, ac[a]) for a in ac if ac[a] != mc])