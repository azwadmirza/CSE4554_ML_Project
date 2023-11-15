def find_series_id(name):
    """Looks up the tvdb id for a series"""
    try:
        series = TVDBRequest().get('search/series', name=name)
    except requests.RequestException as e:
        raise LookupError('Unable to get search results for %s: %s' % (name, e))

    series_list = []

    name = name.lower()

    for s in series:
        # Exact match
        if s.get('seriesName').lower() == name:
            return s['id']
        if s['firstAired']:
            series_list.append((s['firstAired'], s['id']))

    # If there is no exact match, sort by airing date and pick the latest
    if series_list:
        series_list.sort(key=lambda s: s[0], reverse=True)
        return series_list[0][1]
    else:
        raise LookupError('No results for `%s`' % name)