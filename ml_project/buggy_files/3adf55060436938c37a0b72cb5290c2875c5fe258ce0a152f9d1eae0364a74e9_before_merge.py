        def commit_channel_torrent(self, new_start_timestamp=None):
            """
            Collect new/uncommitted and marked for deletion metadata entries, commit them to a channel torrent and
            remove the obsolete entries if the commit succeeds.
            :return The new infohash, should be used to update the downloads
            """
            new_infohash = None
            torrent = None
            md_list = self.staged_entries_list
            if not md_list:
                return None

            try:
                update_dict, torrent = self.update_channel_torrent(md_list)
            except IOError:
                self._logger.error(
                    "Error during channel torrent commit, not going to garbage collect the channel. Channel %s",
                    hexlify(str(self.public_key)))
            else:
                if new_start_timestamp:
                    update_dict['start_timestamp'] = new_start_timestamp
                new_infohash = update_dict['infohash'] if self.infohash != update_dict['infohash'] else None
                self.update_metadata(update_dict)
                self.local_version = self.timestamp
                # Change status of committed metadata and clean up obsolete TODELETE entries
                for g in md_list:
                    if g.status in [NEW, UPDATED]:
                        g.status = COMMITTED
                    elif g.status == TODELETE:
                        g.delete()

                # Write the channel mdblob to disk
                self.to_file(os.path.join(self._channels_dir, self.dir_name + BLOB_EXTENSION))

                self._logger.info("Channel %s committed with %i new entries. New version is %i",
                                  hexlify(str(self.public_key)), len(md_list), update_dict['timestamp'])
            return torrent