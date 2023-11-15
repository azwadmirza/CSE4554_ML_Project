def prepare_lookup_for_pytvmaze(**lookup_params):
    """
    Return a dict of params which is valid with pytvmaze get_show method
    :param lookup_params: Search parameters
    :return: Dict of pytvmaze recognizable key words
    """
    prepared_params = {}
    title = None
    year_match = None
    series_name = lookup_params.get('series_name') or lookup_params.get('show_name') or lookup_params.get('title')
    if series_name:
        title, year_match = split_title_year(series_name)
    # Support for when title is just a number
    if not title:
        title = series_name

    network = lookup_params.get('network') or lookup_params.get('trakt_series_network')
    country = lookup_params.get('country') or lookup_params.get('trakt_series_country')
    language = lookup_params.get('language')

    prepared_params['maze_id'] = lookup_params.get('tvmaze_id')
    prepared_params['tvdb_id'] = lookup_params.get('tvdb_id') or lookup_params.get('trakt_series_tvdb_id')
    prepared_params['tvrage_id'] = lookup_params.get('tvrage_id') or lookup_params.get('trakt_series_tvrage_id')
    prepared_params['imdb_id'] = lookup_params.get('imdb_id')
    prepared_params['show_name'] = native_str_to_text(title, encoding='utf-8') if title else None
    prepared_params['show_year'] = lookup_params.get('trakt_series_year') or lookup_params.get(
        'year') or lookup_params.get('imdb_year') or year_match

    prepared_params['show_network'] = native_str_to_text(network, encoding='utf8') if network else None
    prepared_params['show_country'] = native_str_to_text(country, encoding='utf8') if country else None
    prepared_params['show_language'] = native_str_to_text(language, encoding='utf8') if language else None

    # Include cast information by default
    prepared_params['embed'] = 'cast'

    return prepared_params