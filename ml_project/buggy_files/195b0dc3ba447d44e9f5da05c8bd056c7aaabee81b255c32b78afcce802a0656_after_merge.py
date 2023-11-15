def _convert_mpd_data(data, tracks, music_dir):
    if not data:
        return

    track_kwargs = {}
    album_kwargs = {}
    artist_kwargs = {}
    albumartist_kwargs = {}

    if 'track' in data:
        if '/' in data['track']:
            album_kwargs['num_tracks'] = int(data['track'].split('/')[1])
            track_kwargs['track_no'] = int(data['track'].split('/')[0])
        else:
            track_kwargs['track_no'] = int(data['track'])

    if 'artist' in data:
        artist_kwargs['name'] = data['artist']
        albumartist_kwargs['name'] = data['artist']

    if 'albumartist' in data:
        albumartist_kwargs['name'] = data['albumartist']

    if 'album' in data:
        album_kwargs['name'] = data['album']

    if 'title' in data:
        track_kwargs['name'] = data['title']

    if 'date' in data:
        track_kwargs['date'] = data['date']

    if 'musicbrainz_trackid' in data:
        track_kwargs['musicbrainz_id'] = data['musicbrainz_trackid']

    if 'musicbrainz_albumid' in data:
        album_kwargs['musicbrainz_id'] = data['musicbrainz_albumid']

    if 'musicbrainz_artistid' in data:
        artist_kwargs['musicbrainz_id'] = data['musicbrainz_artistid']

    if 'musicbrainz_albumartistid' in data:
        albumartist_kwargs['musicbrainz_id'] = (
            data['musicbrainz_albumartistid'])

    if artist_kwargs:
        artist = Artist(**artist_kwargs)
        track_kwargs['artists'] = [artist]

    if albumartist_kwargs:
        albumartist = Artist(**albumartist_kwargs)
        album_kwargs['artists'] = [albumartist]

    if album_kwargs:
        album = Album(**album_kwargs)
        track_kwargs['album'] = album

    if data['file'][0] == '/':
        path = data['file'][1:]
    else:
        path = data['file']
    path = urllib.unquote(path.encode('utf-8'))

    if isinstance(music_dir, unicode):
        music_dir = music_dir.encode('utf-8')

    # Make sure we only pass bytestrings to path_to_uri to avoid implicit
    # decoding of bytestrings to unicode strings
    track_kwargs['uri'] = path_to_uri(music_dir, path)

    track_kwargs['length'] = int(data.get('time', 0)) * 1000

    track = Track(**track_kwargs)
    tracks.add(track)