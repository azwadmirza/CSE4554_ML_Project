def _parse_requirement_line(
    line,  # type: LogicalLine
    basepath=None,  # type: Optional[str]
):
    # type: (...) -> ParsedRequirement

    basepath = basepath or os.getcwd()

    editable, processed_text = _strip_requirement_options(line)
    project_name, direct_reference_url = _split_direct_references(processed_text)
    parsed_url = urlparse.urlparse(direct_reference_url or processed_text)

    # Handle non local URLs (Pip proprietary).
    if _is_recognized_non_local_pip_url_scheme(parsed_url.scheme):
        project_name_extras_and_marker = _try_parse_fragment_project_name_and_marker(
            parsed_url.fragment
        )
        project_name, extras, marker = (
            project_name_extras_and_marker
            if project_name_extras_and_marker
            else (project_name, None, None)
        )
        specifier = None  # type: Optional[SpecifierSet]
        if not project_name:
            project_name_and_specifier = _try_parse_project_name_and_specifier_from_path(
                parsed_url.path
            )
            if project_name_and_specifier is not None:
                project_name = project_name_and_specifier.project_name
                specifier = project_name_and_specifier.specifier
        if project_name is None:
            raise ParseError(
                line,
                (
                    "Could not determine a project name for URL requirement {}, consider using "
                    "#egg=<project name>."
                ),
            )
        url = parsed_url._replace(fragment="").geturl()
        requirement = parse_requirement_from_project_name_and_specifier(
            project_name,
            extras=extras,
            specifier=specifier,
            marker=marker,
        )
        return URLRequirement.create(line, url, requirement, editable=editable)

    # Handle local archives and project directories via path or file URL (Pip proprietary).
    local_requirement = parsed_url._replace(scheme="").geturl()
    project_name_extras_and_marker = _try_parse_pip_local_formats(
        local_requirement, basepath=basepath
    )
    maybe_abs_path, extras, marker = (
        project_name_extras_and_marker
        if project_name_extras_and_marker
        else (project_name, None, None)
    )
    if maybe_abs_path is not None and any(
        os.path.isfile(os.path.join(maybe_abs_path, *p))
        for p in ((), ("setup.py",), ("pyproject.toml",))
    ):
        archive_or_project_path = os.path.realpath(maybe_abs_path)
        if os.path.isdir(archive_or_project_path):
            return LocalProjectRequirement.create(
                line,
                archive_or_project_path,
                extras=extras,
                marker=marker,
                editable=editable,
            )
        requirement = parse_requirement_from_dist(
            archive_or_project_path, extras=extras, marker=marker
        )
        return URLRequirement.create(line, archive_or_project_path, requirement, editable=editable)

    # Handle PEP-440. See: https://www.python.org/dev/peps/pep-0440.
    #
    # The `pkg_resources.Requirement.parse` method does all of this for us (via
    # `packaging.requirements.Requirement`) except for the handling of PEP-440 direct url
    # references; which we handled above and won't encounter here.
    try:
        return PyPIRequirement.create(line, Requirement.parse(processed_text), editable=editable)
    except RequirementParseError as e:
        raise ParseError(
            line, "Problem parsing {!r} as a requirement: {}".format(processed_text, e)
        )