    def get_album_info(self, result):
        """Returns an AlbumInfo object for a discogs Release object.
        """
        # Explicitly reload the `Release` fields, as they might not be yet
        # present if the result is from a `discogs_client.search()`.
        if not result.data.get('artists'):
            result.refresh()

        # Sanity check for required fields. The list of required fields is
        # defined at Guideline 1.3.1.a, but in practice some releases might be
        # lacking some of these fields. This function expects at least:
        # `artists` (>0), `title`, `id`, `tracklist` (>0)
        # https://www.discogs.com/help/doc/submission-guidelines-general-rules
        if not all([result.data.get(k) for k in ['artists', 'title', 'id',
                                                 'tracklist']]):
            self._log.warn(u"Release does not contain the required fields")
            return None

        artist, artist_id = self.get_artist([a.data for a in result.artists])
        album = re.sub(r' +', ' ', result.title)
        album_id = result.data['id']
        # Use `.data` to access the tracklist directly instead of the
        # convenient `.tracklist` property, which will strip out useful artist
        # information and leave us with skeleton `Artist` objects that will
        # each make an API call just to get the same data back.
        tracks = self.get_tracks(result.data['tracklist'])

        # Extract information for the optional AlbumInfo fields, if possible.
        va = result.data['artists'][0].get('name', '').lower() == 'various'
        year = result.data.get('year')
        mediums = len(set(t.medium for t in tracks))
        country = result.data.get('country')
        data_url = result.data.get('uri')

        # Extract information for the optional AlbumInfo fields that are
        # contained on nested discogs fields.
        albumtype = media = label = catalogno = None
        if result.data.get('formats'):
            albumtype = ', '.join(
                result.data['formats'][0].get('descriptions', [])) or None
            media = result.data['formats'][0]['name']
        if result.data.get('labels'):
            label = result.data['labels'][0].get('name')
            catalogno = result.data['labels'][0].get('catno')

        # Additional cleanups (various artists name, catalog number, media).
        if va:
            artist = config['va_name'].as_str()
        if catalogno == 'none':
                catalogno = None
        # Explicitly set the `media` for the tracks, since it is expected by
        # `autotag.apply_metadata`, and set `medium_total`.
        for track in tracks:
            track.media = media
            track.medium_total = mediums

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