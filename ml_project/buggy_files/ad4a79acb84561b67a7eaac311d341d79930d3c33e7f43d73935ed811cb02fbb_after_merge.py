def query_from_mpd_list_format(field, mpd_query):
    """
    Converts an MPD ``list`` query to a Mopidy query.
    """
    # NOTE kwargs dict keys must be bytestrings to work on Python < 2.6.5
    # See https://github.com/mopidy/mopidy/issues/302 for details
    if mpd_query is None:
        return {}
    try:
        # shlex does not seem to be friends with unicode objects
        tokens = shlex.split(mpd_query.encode('utf-8'))
    except ValueError as error:
        if str(error) == 'No closing quotation':
            raise MpdArgError('Invalid unquoted character', command='list')
        else:
            raise
    tokens = [t.decode('utf-8') for t in tokens]
    if len(tokens) == 1:
        if field == 'album':
            if not tokens[0]:
                raise ValueError
            return {b'artist': [tokens[0]]}  # See above NOTE
        else:
            raise MpdArgError(
                'should be "Album" for 3 arguments', command='list')
    elif len(tokens) % 2 == 0:
        query = {}
        while tokens:
            key = str(tokens[0].lower())  # See above NOTE
            value = tokens[1]
            tokens = tokens[2:]
            if key not in ('artist', 'album', 'date', 'genre'):
                raise MpdArgError('not able to parse args', command='list')
            if not value:
                raise ValueError
            if key in query:
                query[key].append(value)
            else:
                query[key] = [value]
        return query
    else:
        raise MpdArgError('not able to parse args', command='list')