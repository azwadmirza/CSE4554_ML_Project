        def __init__(self, *args, **kwargs):
            # Free-for-all entries require special treatment
            if "public_key" in kwargs and kwargs["public_key"] == NULL_KEY:
                # To produce a relatively unique id_ we take a few bytes of the infohash and convert it to a number.
                # abs is necessary as the conversion can produce a negative value, and we do not support that.
                kwargs["id_"] = kwargs["id_"] if "id_" in kwargs else infohash_to_id(kwargs["infohash"])

            if "health" not in kwargs and "infohash" in kwargs:
                kwargs["health"] = db.TorrentState.get(infohash=kwargs["infohash"]) or db.TorrentState(
                    infohash=kwargs["infohash"])
            if 'xxx' not in kwargs:
                kwargs["xxx"] = default_xxx_filter.isXXXTorrentMetadataDict(kwargs)

            super(TorrentMetadata, self).__init__(*args, **kwargs)

            if 'tracker_info' in kwargs:
                self.add_tracker(kwargs["tracker_info"])