    def get_album_info(self, result):
        """Returns an AlbumInfo object for a discogs Release object.
        """
        artist, artist_id = self.get_artist([a.data for a in result.artists])
        album = re.sub(r' +', ' ', result.title)
        album_id = result.data['id']
        # Use `.data` to access the tracklist directly instead of the
        # convenient `.tracklist` property, which will strip out useful artist
        # information and leave us with skeleton `Artist` objects that will
        # each make an API call just to get the same data back.
        tracks = self.get_tracks(result.data['tracklist'])
        albumtype = ', '.join(
            result.data['formats'][0].get('descriptions', [])) or None
        va = result.data['artists'][0]['name'].lower() == 'various'
        if va:
            artist = config['va_name'].as_str()
        year = result.data['year']
        label = result.data['labels'][0]['name']
        mediums = len(set(t.medium for t in tracks))
        catalogno = result.data['labels'][0]['catno']
        if catalogno == 'none':
            catalogno = None
        country = result.data.get('country')
        media = result.data['formats'][0]['name']
        # Explicitly set the `media` for the tracks, since it is expected by
        # `autotag.apply_metadata`, and set `medium_total`.
        for track in tracks:
            track.media = media
            track.medium_total = mediums
        data_url = result.data['uri']
        return AlbumInfo(album, album_id, artist, artist_id, tracks, asin=None,
                         albumtype=albumtype, va=va, year=year, month=None,
                         day=None, label=label, mediums=mediums,
                         artist_sort=None, releasegroup_id=None,
                         catalognum=catalogno, script=None, language=None,
                         country=country, albumstatus=None, media=media,
                         albumdisambig=None, artist_credit=None,
                         original_year=None, original_month=None,
                         original_day=None, data_source='Discogs',
                         data_url=data_url)