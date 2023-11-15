    def update_download_hops(self, download, new_hops):
        """
        Update the amount of hops for a specified download. This can be done on runtime.
        """
        infohash = binascii.hexlify(download.tdef.get_infohash())
        self._logger.info("Updating the amount of hops of download %s", infohash)
        yield self.session.remove_download(download)

        # copy the old download_config and change the hop count
        dscfg = download.copy()
        dscfg.set_hops(new_hops)

        self.session.start_download_from_tdef(download.tdef, dscfg)