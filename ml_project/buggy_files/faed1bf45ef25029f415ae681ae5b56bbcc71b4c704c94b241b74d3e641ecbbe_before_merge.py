    def get_status(self):
        """ Returns the status of the torrent.
        @return DLSTATUS_* """
        if not self.lt_status:
            return (DLSTATUS_CIRCUITS if not self.download.session.tunnel_community
                    or self.download.session.tunnel_community.get_candidates(PEER_FLAG_EXIT_ANY)
                    else DLSTATUS_EXIT_NODES) if self.download.config.get_hops() > 0 else DLSTATUS_WAITING4HASHCHECK
        elif self.get_error():
            return DLSTATUS_STOPPED_ON_ERROR
        return DLSTATUS_MAP[self.lt_status.state] if not self.lt_status.paused else DLSTATUS_STOPPED