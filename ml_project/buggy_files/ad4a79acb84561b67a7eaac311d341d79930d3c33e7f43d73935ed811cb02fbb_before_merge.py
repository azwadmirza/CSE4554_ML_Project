def query_from_mpd_list_format(field, mpd_query):
    """
    Converts an MPD ``list`` query to a Mopidy query.
    """
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
            return {'artist': [tokens[0]]}
        else:
            raise MpdArgError(
                'should be "Album" for 3 arguments', command='list')
    elif len(tokens) % 2 == 0:
        query = {}
        while tokens:
            key = tokens[0].lower()
            key = str(key)  # Needed for kwargs keys on OS X and Windows
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