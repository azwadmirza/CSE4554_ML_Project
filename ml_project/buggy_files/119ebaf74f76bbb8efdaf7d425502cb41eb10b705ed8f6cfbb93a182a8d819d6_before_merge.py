        def to_simple_dict(self, include_trackers=False):
            """
            Return a basic dictionary with information about the channel.
            """
            epoch = datetime.utcfromtimestamp(0)
            simple_dict = {
                "id": self.id_,
                "public_key": hexlify(self.public_key),
                "name": self.title,
                "infohash": hexlify(self.infohash),
                "size": self.size,
                "category": self.tags,
                "num_seeders": self.health.seeders,
                "num_leechers": self.health.leechers,
                "last_tracker_check": self.health.last_check,
                "updated": int((self.torrent_date - epoch).total_seconds()),
                "status": self.status,
                "type": {REGULAR_TORRENT: 'torrent', CHANNEL_TORRENT: 'channel'}[self.metadata_type]
            }

            if include_trackers:
                simple_dict['trackers'] = [tracker.url for tracker in self.health.trackers]

            return simple_dict