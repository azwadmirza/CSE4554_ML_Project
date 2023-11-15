def track_to_mpd_format(track, position=None, stream_title=None):
    """
    Format track for output to MPD client.

    :param track: the track
    :type track: :class:`mopidy.models.Track` or :class:`mopidy.models.TlTrack`
    :param position: track's position in playlist
    :type position: integer
    :param stream_title: the current streams title
    :type position: string
    :rtype: list of two-tuples
    """
    if isinstance(track, TlTrack):
        (tlid, track) = track
    else:
        (tlid, track) = (None, track)

    if not track.uri:
        logger.warning('Ignoring track without uri')
        return []

    result = [
        ('file', track.uri),
        ('Time', track.length and (track.length // 1000) or 0),
        ('Artist', concat_multi_values(track.artists, 'name')),
        ('Album', track.album and track.album.name or ''),
    ]

    if stream_title is not None:
        result.append(('Title', stream_title))
        if track.name:
            result.append(('Name', track.name))
    else:
        result.append(('Title', track.name or ''))

    if track.date:
        result.append(('Date', track.date))

    if track.album is not None and track.album.num_tracks is not None:
        result.append(('Track', '%d/%d' % (
            track.track_no or 0, track.album.num_tracks)))
    else:
        result.append(('Track', track.track_no or 0))
    if position is not None and tlid is not None:
        result.append(('Pos', position))
        result.append(('Id', tlid))
    if track.album is not None and track.album.musicbrainz_id is not None:
        result.append(('MUSICBRAINZ_ALBUMID', track.album.musicbrainz_id))

    if track.album is not None and track.album.artists:
        result.append(
            ('AlbumArtist', concat_multi_values(track.album.artists, 'name')))
        musicbrainz_ids = concat_multi_values(
            track.album.artists, 'musicbrainz_id')
        if musicbrainz_ids:
            result.append(('MUSICBRAINZ_ALBUMARTISTID', musicbrainz_ids))

    if track.artists:
        musicbrainz_ids = concat_multi_values(track.artists, 'musicbrainz_id')
        if musicbrainz_ids:
            result.append(('MUSICBRAINZ_ARTISTID', musicbrainz_ids))

    if track.composers:
        result.append(
            ('Composer', concat_multi_values(track.composers, 'name')))

    if track.performers:
        result.append(
            ('Performer', concat_multi_values(track.performers, 'name')))

    if track.genre:
        result.append(('Genre', track.genre))

    if track.disc_no:
        result.append(('Disc', track.disc_no))

    if track.last_modified:
        datestring = datetime.datetime.utcfromtimestamp(
            track.last_modified // 1000).isoformat()
        result.append(('Last-Modified', datestring + 'Z'))

    if track.musicbrainz_id is not None:
        result.append(('MUSICBRAINZ_TRACKID', track.musicbrainz_id))

    if track.album and track.album.uri:
        result.append(('X-AlbumUri', track.album.uri))
    if track.album and track.album.images:
        images = ';'.join(i for i in track.album.images if i != '')
        result.append(('X-AlbumImage', images))

    result = [element for element in result if _has_value(*element)]

    return result