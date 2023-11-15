def fuzzy_url(urlstr: str,
              cwd: str = None,
              relative: bool = False,
              do_search: bool = True,
              force_search: bool = False) -> QUrl:
    """Get a QUrl based on a user input which is URL or search term.

    Args:
        urlstr: URL to load as a string.
        cwd: The current working directory, or None.
        relative: Whether to resolve relative files.
        do_search: Whether to perform a search on non-URLs.
        force_search: Whether to force a search even if the content can be
                      interpreted as a URL or a path.

    Return:
        A target QUrl to a search page or the original URL.
    """
    urlstr = urlstr.strip()
    path = get_path_if_valid(urlstr, cwd=cwd, relative=relative,
                             check_exists=True)

    if not force_search and path is not None:
        url = QUrl.fromLocalFile(path)
    elif force_search or (do_search and not is_url(urlstr)):
        # probably a search term
        log.url.debug("URL is a fuzzy search term")
        try:
            url = _get_search_url(urlstr)
        except ValueError:  # invalid search engine
            url = qurl_from_user_input(urlstr)
    else:  # probably an address
        log.url.debug("URL is a fuzzy address")
        url = qurl_from_user_input(urlstr)
    log.url.debug("Converting fuzzy term {!r} to URL -> {}".format(
        urlstr, url.toDisplayString()))
    ensure_valid(url)
    return url