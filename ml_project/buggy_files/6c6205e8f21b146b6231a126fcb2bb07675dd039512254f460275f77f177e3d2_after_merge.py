        def to_simple_dict(self):
            """
            Return a basic dictionary with information about the channel.
            """
            epoch = datetime.utcfromtimestamp(0)

            return {
                "id": self.rowid,
                "public_key": hexlify(self.public_key),
                "name": self.title,
                "torrents": self.contents_len,
                "subscribed": self.subscribed,
                "votes": self.votes,
                "status": self.status,
                "updated": int((self.torrent_date - epoch).total_seconds()),

                # TODO: optimize this?
                "my_channel": database_blob(self._my_key.pub().key_to_bin()[10:]) == database_blob(self.public_key)
            }