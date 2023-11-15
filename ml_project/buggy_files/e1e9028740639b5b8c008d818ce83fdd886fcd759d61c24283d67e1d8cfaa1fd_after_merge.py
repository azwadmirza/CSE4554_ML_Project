def purge_page_from_cache(page, backend_settings=None, backends=None):
    page_url = page.full_url
    if page_url is None:  # nothing to be done if the page has no routable URL
        return

    for backend_name, backend in get_backends(backend_settings=backend_settings, backends=backends).items():
        # Purge cached paths from cache
        for path in page.specific.get_cached_paths():
            logger.info("[%s] Purging URL: %s", backend_name, page_url + path[1:])
            backend.purge(page_url + path[1:])