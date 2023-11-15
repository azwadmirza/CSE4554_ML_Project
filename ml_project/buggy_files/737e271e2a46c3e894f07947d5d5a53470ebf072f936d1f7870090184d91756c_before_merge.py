    def load_checkpoint(self):
        """
        Restart Downloads from a saved checkpoint, if any. Note that we fetch information from the user download
        choices since it might be that a user has stopped a download. In that case, the download should not be
        resumed immediately when being loaded by libtorrent.
        """
        initialdlstatus_dict = {}
        for infohash, state in self.tribler_config.get_download_states().iteritems():
            if state == 'stop':
                initialdlstatus_dict[infohash] = DLSTATUS_STOPPED

        self.lm.load_checkpoint(initialdlstatus_dict=initialdlstatus_dict)