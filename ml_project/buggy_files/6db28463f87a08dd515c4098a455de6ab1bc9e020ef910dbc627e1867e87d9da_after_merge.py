def _convert_mpd_data(data, tracks, music_dir):
    if not data:
        return

    # NOTE kwargs dict keys must be bytestrings to work on Python < 2.6.5
    # See https://github.com/mopidy/mopidy/issues/302 for details.

    track_kwargs = {}
    album_kwargs = {}
    artist_kwargs = {}
    albumartist_kwargs = {}

    if 'track' in data:
        if '/' in data['track']:
            album_kwargs[b'num_tracks'] = int(data['track'].split('/')[1])
            track_kwargs[b'track_no'] = int(data['track'].split('/')[0])
        else:
            track_kwargs[b'track_no'] = int(data['track'])

    if 'artist' in data:
        artist_kwargs[b'name'] = data['artist']
        albumartist_kwargs[b'name'] = data['artist']

    if 'albumartist' in data:
        albumartist_kwargs[b'name'] = data['albumartist']

    if 'album' in data:
        album_kwargs[b'name'] = data['album']

    if 'title' in data:
        track_kwargs[b'name'] = data['title']

    if 'date' in data:
        track_kwargs[b'date'] = data['date']

    if 'musicbrainz_trackid' in data:
        track_kwargs[b'musicbrainz_id'] = data['musicbrainz_trackid']

    if 'musicbrainz_albumid' in data:
        album_kwargs[b'musicbrainz_id'] = data['musicbrainz_albumid']

    if 'musicbrainz_artistid' in data:
        artist_kwargs[b'musicbrainz_id'] = data['musicbrainz_artistid']

    if 'musicbrainz_albumartistid' in data:
        albumartist_kwargs[b'musicbrainz_id'] = (
            data['musicbrainz_albumartistid'])

    if data['file'][0] == '/':
        path = data['file'][1:]
    else:
        path = data['file']
    path = urllib.unquote(path)

    if artist_kwargs:
        artist = Artist(**artist_kwargs)
        track_kwargs[b'artists'] = [artist]

    if albumartist_kwargs:
        albumartist = Artist(**albumartist_kwargs)
        album_kwargs[b'artists'] = [albumartist]

    if album_kwargs:
        album = Album(**album_kwargs)
        track_kwargs[b'album'] = album

    track_kwargs[b'uri'] = path_to_uri(music_dir, path)
    track_kwargs[b'length'] = int(data.get('time', 0)) * 1000

    track = Track(**track_kwargs)
    tracks.add(track)