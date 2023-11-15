    def __get_metadata(self):
        """http://xmms2.org/wiki/MPRIS_Metadata"""

        metadata = {}
        metadata["mpris:trackid"] = self.__get_current_track_id()

        song = app.player.info
        if not song:
            return metadata

        metadata["mpris:length"] = dbus.Int64(song("~#length") * 10 ** 6)

        self.__cover = cover = app.cover_manager.get_cover(song)
        is_temp = False
        if cover:
            name = cover.name
            is_temp = name.startswith(tempfile.gettempdir())
            # This doesn't work for embedded images.. the file gets unlinked
            # after loosing the file handle
            metadata["mpris:artUrl"] = fsn2uri(name)

        if not is_temp:
            self.__cover = None

        # All list values
        list_val = {"artist": "artist", "albumArtist": "albumartist",
            "comment": "comment", "composer": "composer", "genre": "genre",
            "lyricist": "lyricist"}
        for xesam, tag in iteritems(list_val):
            vals = song.list(tag)
            if vals:
                metadata["xesam:" + xesam] = listmap(unival, vals)

        # All single values
        sing_val = {"album": "album", "title": "title", "asText": "~lyrics"}
        for xesam, tag in iteritems(sing_val):
            vals = song.comma(tag)
            if vals:
                metadata["xesam:" + xesam] = unival(vals)

        # URI
        metadata["xesam:url"] = song("~uri")

        # Integers
        num_val = {"audioBPM": "bpm", "discNumber": "disc",
                   "trackNumber": "track", "useCount": "playcount"}

        for xesam, tag in iteritems(num_val):
            val = song("~#" + tag, None)
            if val is not None:
                metadata["xesam:" + xesam] = int(val)

        # Rating
        metadata["xesam:userRating"] = float(song("~#rating"))

        # Dates
        ISO_8601_format = "%Y-%m-%dT%H:%M:%S"
        tuple_time = time.gmtime(song("~#lastplayed"))
        iso_time = time.strftime(ISO_8601_format, tuple_time)
        metadata["xesam:lastUsed"] = iso_time

        year = song("~year")
        if year:
            try:
                tuple_time = time.strptime(year, "%Y")
                iso_time = time.strftime(ISO_8601_format, tuple_time)
            except ValueError:
                pass
            else:
                metadata["xesam:contentCreated"] = iso_time

        return metadata