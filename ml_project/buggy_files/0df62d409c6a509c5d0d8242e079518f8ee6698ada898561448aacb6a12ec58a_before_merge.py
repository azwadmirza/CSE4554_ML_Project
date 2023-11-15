    def CompressShares(self, sharestype):

        if sharestype == "normal":
            streams = self.config.sections["transfers"]["sharedfilesstreams"]
        elif sharestype == "buddy":
            streams = self.config.sections["transfers"]["bsharedfilesstreams"]

        if streams is None:
            message = _("ERROR: No %(type)s shares database available") % {"type": sharestype}
            print(message)
            self.logMessage(message, None)
            return

        m = slskmessages.SharedFileList(None, streams)
        m.makeNetworkMessage(nozlib=0, rebuild=True)

        if sharestype == "normal":
            self.CompressedSharesNormal = m
        elif sharestype == "buddy":
            self.CompressedSharesBuddy = m