        def _put_health_entries_in_db():
            with db_session(immediate=True):
                for infohash, seeders, leechers, last_check in all_torrents:
                    torrent_state = self.metadata_store.TorrentState.get(infohash=infohash)
                    if torrent_state and last_check > torrent_state.last_check:
                        # Replace current information
                        torrent_state.seeders = seeders
                        torrent_state.leechers = leechers
                        torrent_state.last_check = last_check
                    elif not torrent_state:
                        _ = self.metadata_store.TorrentState(infohash=infohash, seeders=seeders,
                                                             leechers=leechers, last_check=last_check)

            self.metadata_store.disconnect_thread()