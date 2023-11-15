    def copy_metainfo_to_torrent_parameters(self):
        """
        Populate the torrent_parameters dictionary with information from the metainfo.
        """
        for key in ["comment", "created by", "creation date", "announce", "announce-list", "nodes",
                    "httpseeds", "urllist"]:
            if self.metainfo and key in self.metainfo:
                self.torrent_parameters[key] = self.metainfo[key]

        infokeys = ['name', 'piece length']
        for key in infokeys:
            if self.metainfo and key in self.metainfo[b'info']:
                self.torrent_parameters[key] = self.metainfo[b'info'][key]