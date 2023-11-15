        def on_torrent_added(handle):
            self.handle = handle

            if self.handle.is_valid():
                self.set_selected_files()

                user_stopped = pstate.get('download_defaults', 'user_stopped') if pstate else False

                # If we lost resume_data always resume download in order to force checking
                if not user_stopped or not resume_data:
                    self.handle.resume()

                    # If we only needed to perform checking, pause download after it is complete
                    self.pause_after_next_hashcheck = user_stopped

                self.set_vod_mode(self.get_mode() == DLMODE_VOD)

                # Limit the amount of connections if we have specified that
                self.handle.set_max_connections(self.session.config.get_libtorrent_max_conn_download())
                return self