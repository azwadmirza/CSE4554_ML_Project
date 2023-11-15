def process_line(
    line,  # type: Text
    filename,  # type: str
    line_number,  # type: int
    finder=None,  # type: Optional[PackageFinder]
    comes_from=None,  # type: Optional[str]
    options=None,  # type: Optional[optparse.Values]
    session=None,  # type: Optional[PipSession]
    wheel_cache=None,  # type: Optional[WheelCache]
    use_pep517=None,  # type: Optional[bool]
    constraint=False,  # type: bool
):
    # type: (...) -> Iterator[InstallRequirement]
    """Process a single requirements line; This can result in creating/yielding
    requirements, or updating the finder.

    For lines that contain requirements, the only options that have an effect
    are from SUPPORTED_OPTIONS_REQ, and they are scoped to the
    requirement. Other options from SUPPORTED_OPTIONS may be present, but are
    ignored.

    For lines that do not contain requirements, the only options that have an
    effect are from SUPPORTED_OPTIONS. Options from SUPPORTED_OPTIONS_REQ may
    be present, but are ignored. These lines may contain multiple options
    (although our docs imply only one is supported), and all our parsed and
    affect the finder.

    :param constraint: If True, parsing a constraints file.
    :param options: OptionParser options that we may update
    """
    parser = build_parser(line)
    defaults = parser.get_default_values()
    defaults.index_url = None
    if finder:
        defaults.format_control = finder.format_control
    args_str, options_str = break_args_options(line)
    # Prior to 2.7.3, shlex cannot deal with unicode entries
    if sys.version_info < (2, 7, 3):
        # https://github.com/python/mypy/issues/1174
        options_str = options_str.encode('utf8')  # type: ignore
    # https://github.com/python/mypy/issues/1174
    opts, _ = parser.parse_args(
        shlex.split(options_str), defaults)  # type: ignore

    # preserve for the nested code path
    line_comes_from = '%s %s (line %s)' % (
        '-c' if constraint else '-r', filename, line_number,
    )

    # yield a line requirement
    if args_str:
        isolated = options.isolated_mode if options else False
        if options:
            cmdoptions.check_install_build_global(options, opts)
        # get the options that apply to requirements
        req_options = {}
        for dest in SUPPORTED_OPTIONS_REQ_DEST:
            if dest in opts.__dict__ and opts.__dict__[dest]:
                req_options[dest] = opts.__dict__[dest]
        line_source = 'line {} of {}'.format(line_number, filename)
        yield install_req_from_line(
            args_str,
            comes_from=line_comes_from,
            use_pep517=use_pep517,
            isolated=isolated,
            options=req_options,
            wheel_cache=wheel_cache,
            constraint=constraint,
            line_source=line_source,
        )

    # yield an editable requirement
    elif opts.editables:
        isolated = options.isolated_mode if options else False
        yield install_req_from_editable(
            opts.editables[0], comes_from=line_comes_from,
            use_pep517=use_pep517,
            constraint=constraint, isolated=isolated, wheel_cache=wheel_cache
        )

    # parse a nested requirements file
    elif opts.requirements or opts.constraints:
        if opts.requirements:
            req_path = opts.requirements[0]
            nested_constraint = False
        else:
            req_path = opts.constraints[0]
            nested_constraint = True
        # original file is over http
        if SCHEME_RE.search(filename):
            # do a url join so relative paths work
            req_path = urllib_parse.urljoin(filename, req_path)
        # original file and nested file are paths
        elif not SCHEME_RE.search(req_path):
            # do a join so relative paths work
            req_path = os.path.join(os.path.dirname(filename), req_path)
        # TODO: Why not use `comes_from='-r {} (line {})'` here as well?
        parsed_reqs = parse_requirements(
            req_path, finder, comes_from, options, session,
            constraint=nested_constraint, wheel_cache=wheel_cache
        )
        for req in parsed_reqs:
            yield req

    # percolate hash-checking option upward
    elif opts.require_hashes:
        options.require_hashes = opts.require_hashes

    # set finder options
    elif finder:
        if opts.index_url:
            finder.index_urls = [opts.index_url]
        if opts.no_index is True:
            finder.index_urls = []
        if opts.extra_index_urls:
            finder.index_urls.extend(opts.extra_index_urls)
        if opts.find_links:
            # FIXME: it would be nice to keep track of the source
            # of the find_links: support a find-links local path
            # relative to a requirements file.
            value = opts.find_links[0]
            req_dir = os.path.dirname(os.path.abspath(filename))
            relative_to_reqs_file = os.path.join(req_dir, value)
            if os.path.exists(relative_to_reqs_file):
                value = relative_to_reqs_file
            finder.find_links.append(value)
        if opts.pre:
            finder.set_allow_all_prereleases()
        for host in opts.trusted_hosts or []:
            source = 'line {} of {}'.format(line_number, filename)
            finder.add_trusted_host(host, source=source)