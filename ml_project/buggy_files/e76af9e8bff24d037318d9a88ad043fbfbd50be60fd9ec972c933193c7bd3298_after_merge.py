        def consolidate_channel_torrent(self):
            """
            Delete the channel dir contents and create it anew.
            Use it to consolidate fragmented channel torrent directories.
            :param key: The public/private key, used to sign the data
            """

            self.commit_channel_torrent()

            folder = os.path.join(self._channels_dir, self.dir_name)
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                # We only remove mdblobs and leave the rest as it is
                if filename.endswith(BLOB_EXTENSION) or filename.endswith(BLOB_EXTENSION + '.lz4'):
                    os.unlink(file_path)

            # Channel should get a new starting timestamp and its contents should get higher timestamps
            start_timestamp = self._clock.tick()
            for g in self.contents:
                if g.status == COMMITTED:
                    g.status = UPDATED
                    g.timestamp = self._clock.tick()
                    g.sign()

            return self.commit_channel_torrent(new_start_timestamp=start_timestamp)