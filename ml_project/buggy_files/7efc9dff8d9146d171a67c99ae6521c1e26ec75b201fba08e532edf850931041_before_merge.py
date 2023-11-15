def _follow(config_line, url_context, use_dir_urls, header=None, title=None):

    if isinstance(config_line, str):
        path = os.path.normpath(config_line)
        page = _path_to_page(path, title, url_context, use_dir_urls)

        if header:
            page.ancestors = [header]
            header.children.append(page)

        yield page
        raise StopIteration

    elif not isinstance(config_line, dict):
        msg = ("Line in 'page' config is of type {0}, dict or string "
               "expected. Config: {1}").format(type(config_line), config_line)
        raise exceptions.ConfigurationError(msg)

    if len(config_line) > 1:
        raise exceptions.ConfigurationError(
            "Page configs should be in the format 'name: markdown.md'. The "
            "config contains an invalid entry: {0}".format(config_line))
    elif len(config_line) == 0:
        log.warning("Ignoring empty line in the pages config.")
        raise StopIteration

    next_cat_or_title, subpages_or_path = next(iter(config_line.items()))

    if isinstance(subpages_or_path, str):
        path = subpages_or_path
        for sub in _follow(path, url_context, use_dir_urls, header=header, title=next_cat_or_title):
            yield sub
        raise StopIteration

    elif not isinstance(subpages_or_path, list):
        msg = ("Line in 'page' config is of type {0}, list or string "
               "expected for sub pages. Config: {1}"
               ).format(type(config_line), config_line)
        raise exceptions.ConfigurationError(msg)

    next_header = Header(title=next_cat_or_title, children=[])
    if header:
        next_header.ancestors = [header]
        header.children.append(next_header)
    yield next_header

    subpages = subpages_or_path

    for subpage in subpages:
        for sub in _follow(subpage, url_context, use_dir_urls, next_header):
            yield sub