def _generate_site_navigation(pages_config, url_context, use_directory_urls=True):
    """
    Returns a list of Page and Header instances that represent the
    top level site navigation.
    """
    nav_items = []
    pages = []
    previous = None

    for config_line in pages_config:
        if isinstance(config_line, str):
            path = os.path.normpath(config_line)
            title, child_title = None, None
        elif len(config_line) in (1, 2, 3):
            # Pad any items that don't exist with 'None'
            padded_config = (list(config_line) + [None, None])[:3]
            path, title, child_title = padded_config
            path = os.path.normpath(path)
        else:
            msg = (
                "Line in 'page' config contained %d items.  "
                "Expected 1, 2 or 3 strings." % len(config_line)
            )
            raise exceptions.ConfigurationError(msg)

        # If both the title and child_title are None, then we
        # have just been given a path. If that path contains a /
        # then lets automatically nest it.
        if title is None and child_title is None and os.path.sep in path:
            filename = path.split(os.path.sep)[-1]
            child_title = filename_to_title(filename)

        if title is None:
            filename = path.split(os.path.sep)[0]
            title = filename_to_title(filename)

        # If we don't have a child title but the other title is the same, we
        # should be within a section and the child title needs to be inferred
        # from the filename.
        if len(nav_items) and title == nav_items[-1].title == title and child_title is None:
            filename = path.split(os.path.sep)[-1]
            child_title = filename_to_title(filename)

        url = utils.get_url_path(path, use_directory_urls)

        if not child_title:
            # New top level page.
            page = Page(title=title, url=url, path=path, url_context=url_context)
            nav_items.append(page)
        elif not nav_items or (nav_items[-1].title != title):
            # New second level page.
            page = Page(title=child_title, url=url, path=path, url_context=url_context)
            header = Header(title=title, children=[page])
            nav_items.append(header)
            page.ancestors = [header]
        else:
            # Additional second level page.
            page = Page(title=child_title, url=url, path=path, url_context=url_context)
            header = nav_items[-1]
            header.children.append(page)
            page.ancestors = [header]

        # Add in previous and next information.
        if previous:
            page.previous_page = previous
            previous.next_page = page
        previous = page

        pages.append(page)

    return (nav_items, pages)