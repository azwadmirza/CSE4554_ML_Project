def install_req_from_line(
    name,  # type: str
    comes_from=None,  # type: Optional[Union[str, InstallRequirement]]
    use_pep517=None,  # type: Optional[bool]
    isolated=False,  # type: bool
    options=None,  # type: Optional[Dict[str, Any]]
    wheel_cache=None,  # type: Optional[WheelCache]
    constraint=False,  # type: bool
    line_source=None,  # type: Optional[str]
):
    # type: (...) -> InstallRequirement
    """Creates an InstallRequirement from a name, which might be a
    requirement, directory containing 'setup.py', filename, or URL.

    :param line_source: An optional string describing where the line is from,
        for logging purposes in case of an error.
    """
    if is_url(name):
        marker_sep = '; '
    else:
        marker_sep = ';'
    if marker_sep in name:
        name, markers_as_string = name.split(marker_sep, 1)
        markers_as_string = markers_as_string.strip()
        if not markers_as_string:
            markers = None
        else:
            markers = Marker(markers_as_string)
    else:
        markers = None
    name = name.strip()
    req_as_string = None
    path = os.path.normpath(os.path.abspath(name))
    link = None
    extras_as_string = None

    if is_url(name):
        link = Link(name)
    else:
        p, extras_as_string = _strip_extras(path)
        looks_like_dir = os.path.isdir(p) and (
            os.path.sep in name or
            (os.path.altsep is not None and os.path.altsep in name) or
            name.startswith('.')
        )
        if looks_like_dir:
            if not is_installable_dir(p):
                raise InstallationError(
                    "Directory %r is not installable. Neither 'setup.py' "
                    "nor 'pyproject.toml' found." % name
                )
            link = Link(path_to_url(p))
        elif is_archive_file(p):
            if not os.path.isfile(p):
                logger.warning(
                    'Requirement %r looks like a filename, but the '
                    'file does not exist',
                    name
                )
            link = Link(path_to_url(p))

    # it's a local file, dir, or url
    if link:
        # Handle relative file URLs
        if link.scheme == 'file' and re.search(r'\.\./', link.url):
            link = Link(
                path_to_url(os.path.normpath(os.path.abspath(link.path))))
        # wheel file
        if link.is_wheel:
            wheel = Wheel(link.filename)  # can raise InvalidWheelFilename
            req_as_string = "%s==%s" % (wheel.name, wheel.version)
        else:
            # set the req to the egg fragment.  when it's not there, this
            # will become an 'unnamed' requirement
            req_as_string = link.egg_fragment

    # a requirement specifier
    else:
        req_as_string = name

    if extras_as_string:
        extras = Requirement("placeholder" + extras_as_string.lower()).extras
    else:
        extras = ()
    if req_as_string is not None:
        try:
            req = Requirement(req_as_string)
        except InvalidRequirement:
            if os.path.sep in req_as_string:
                add_msg = "It looks like a path."
                add_msg += deduce_helpful_msg(req_as_string)
            elif ('=' in req_as_string and
                  not any(op in req_as_string for op in operators)):
                add_msg = "= is not a valid operator. Did you mean == ?"
            else:
                add_msg = ''
            if line_source is None:
                source = ''
            else:
                source = ' (from {})'.format(line_source)
            msg = (
                'Invalid requirement: {!r}{}'.format(req_as_string, source)
            )
            if add_msg:
                msg += '\nHint: {}'.format(add_msg)
            raise InstallationError(msg)
    else:
        req = None

    return InstallRequirement(
        req, comes_from, link=link, markers=markers,
        use_pep517=use_pep517, isolated=isolated,
        options=options if options else {},
        wheel_cache=wheel_cache,
        constraint=constraint,
        extras=extras,
    )