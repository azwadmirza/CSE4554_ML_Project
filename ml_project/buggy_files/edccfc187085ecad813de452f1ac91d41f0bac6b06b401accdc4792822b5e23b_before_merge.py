    def check_watch_folder(self):
        if not os.path.isdir(self.session.config.get_watch_folder_path()):
            return

        # Make sure that we pass a str to os.walk
        watch_dir = self.session.config.get_watch_folder_path().encode('raw_unicode_escape')

        for root, _, files in os.walk(watch_dir):
            for name in files:
                if not name.endswith(".torrent"):
                    continue

                try:
                    tdef = TorrentDef.load_from_memory(fix_torrent(os.path.join(root, name)))
                except:  # torrent appears to be corrupt
                    self.cleanup_torrent_file(root, name)
                    continue

                infohash = tdef.get_infohash()

                if not self.session.has_download(infohash):
                    self._logger.info("Starting download from torrent file %s", name)
                    dl_config = DefaultDownloadStartupConfig.getInstance().copy()

                    anon_enabled = self.session.config.get_default_anonymity_enabled()
                    default_num_hops = self.session.config.get_default_number_hops()
                    dl_config.set_hops(default_num_hops if anon_enabled else 0)
                    dl_config.set_safe_seeding(self.session.config.get_default_safeseeding_enabled())
                    dl_config.set_dest_dir(self.session.config.get_default_destination_dir())
                    self.session.lm.ltmgr.start_download(tdef=tdef, dconfig=dl_config)