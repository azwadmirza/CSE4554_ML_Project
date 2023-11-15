def _get_search_url(txt):
    """Get a search engine URL for a text.

    Args:
        txt: Text to search for.

    Return:
        The search URL as a QUrl.
    """
    log.url.debug("Finding search engine for {!r}".format(txt))
    engine, term = _parse_search_term(txt)
    assert term
    if engine is None:
        engine = 'DEFAULT'
    template = config.val.url.searchengines[engine]
    url = qurl_from_user_input(template.format(urllib.parse.quote(term)))

    if config.val.url.open_base_url and term in config.val.url.searchengines:
        url = qurl_from_user_input(config.val.url.searchengines[term])
        url.setPath(None)
        url.setFragment(None)
        url.setQuery(None)
    qtutils.ensure_valid(url)
    return url