def resolve_multi(
    requirements=None,
    requirement_files=None,
    constraint_files=None,
    allow_prereleases=False,
    transitive=True,
    interpreters=None,
    platforms=None,
    indexes=None,
    find_links=None,
    network_configuration=None,
    cache=None,
    build=True,
    use_wheel=True,
    compile=False,
    manylinux=None,
    max_parallel_jobs=None,
    ignore_errors=False,
):
    """Resolves all distributions needed to meet requirements for multiple distribution targets.

    The resulting distributions are installed in individual chroots that can be independently added
    to `sys.path`

    :keyword requirements: A sequence of requirement strings.
    :type requirements: list of str
    :keyword requirement_files: A sequence of requirement file paths.
    :type requirement_files: list of str
    :keyword constraint_files: A sequence of constraint file paths.
    :type constraint_files: list of str
    :keyword bool allow_prereleases: Whether to include pre-release and development versions when
      resolving requirements. Defaults to ``False``, but any requirements that explicitly request
      prerelease or development versions will override this setting.
    :keyword bool transitive: Whether to resolve transitive dependencies of requirements.
      Defaults to ``True``.
    :keyword interpreters: If specified, distributions will be resolved for these interpreters, and
      non-wheel distributions will be built against each interpreter. If both `interpreters` and
      `platforms` are ``None`` (the default) or an empty iterable, this defaults to a list
      containing only the current interpreter.
    :type interpreters: list of :class:`pex.interpreter.PythonInterpreter`
    :keyword platforms: An iterable of PEP425-compatible platform strings to resolve distributions
      for, in addition to the platforms of any given interpreters. If any distributions need to be
      built, use the interpreters argument instead, providing the corresponding interpreter.
      However, if any platform matches the current interpreter, the current interpreter will be used
      to build any non-wheels for that platform.
    :type platforms: list of str
    :keyword indexes: A list of urls or paths pointing to PEP 503 compliant repositories to search for
      distributions. Defaults to ``None`` which indicates to use the default pypi index. To turn off
      use of all indexes, pass an empty list.
    :type indexes: list of str
    :keyword find_links: A list or URLs, paths to local html files or directory paths. If URLs or
      local html file paths, these are parsed for links to distributions. If a local directory path,
      its listing is used to discover distributions.
    :type find_links: list of str
    :keyword network_configuration: Configuration for network requests made downloading and building
      distributions.
    :type network_configuration: :class:`pex.network_configuration.NetworkConfiguration`
    :keyword str cache: A directory path to use to cache distributions locally.
    :keyword bool build: Whether to allow building source distributions when no wheel is found.
      Defaults to ``True``.
    :keyword bool use_wheel: Whether to allow resolution of pre-built wheel distributions.
      Defaults to ``True``.
    :keyword bool compile: Whether to pre-compile resolved distribution python sources.
      Defaults to ``False``.
    :keyword str manylinux: The upper bound manylinux standard to support when targeting foreign linux
      platforms. Defaults to ``None``.
    :keyword int max_parallel_jobs: The maximum number of parallel jobs to use when resolving,
      building and installing distributions in a resolve. Defaults to the number of CPUs available.
    :keyword bool ignore_errors: Whether to ignore resolution solver errors. Defaults to ``False``.
    :returns: List of :class:`ResolvedDistribution` instances meeting ``requirements``.
    :raises Unsatisfiable: If ``requirements`` is not transitively satisfiable.
    :raises Untranslatable: If no compatible distributions could be acquired for
      a particular requirement.
    :raises ValueError: If a foreign platform was provided in `platforms`, and `use_wheel=False`.
    :raises ValueError: If `build=False` and `use_wheel=False`.
    """

    # A resolve happens in four stages broken into two phases:
    # 1. Download phase: resolves sdists and wheels in a single operation per distribution target.
    # 2. Install phase:
    #   1. Build local projects and sdists.
    #   2. Install wheels in individual chroots.
    #   3. Calculate the final resolved requirements.
    #
    # You'd think we might be able to just pip install all the requirements, but pexes can be
    # multi-platform / multi-interpreter, in which case only a subset of distributions resolved into
    # the PEX should be activated for the runtime interpreter. Sometimes there are platform specific
    # wheels and sometimes python version specific dists (backports being the common case). As such,
    # we need to be able to add each resolved distribution to the `sys.path` individually
    # (`PEXEnvironment` handles this selective activation at runtime). Since pip install only
    # accepts a single location to install all resolved dists, that won't work.
    #
    # This means we need to separately resolve all distributions, then install each in their own
    # chroot. To do this we use `pip download` for the resolve and download of all needed
    # distributions and then `pip install` to install each distribution in its own chroot.
    #
    # As a complicating factor, the runtime activation scheme relies on PEP 425 tags; i.e.: wheel
    # names. Some requirements are only available or applicable in source form - either via sdist,
    # VCS URL or local projects. As such we need to insert a `pip wheel` step to generate wheels for
    # all requirements resolved in source form via `pip download` / inspection of requirements to
    # discover those that are local directories (local setup.py or pyproject.toml python projects).
    #
    # Finally, we must calculate the pinned requirement corresponding to each distribution we
    # resolved along with any environment markers that control which runtime environments the
    # requirement should be activated in.

    workspace = safe_mkdtemp()

    build_requests, download_results = _download_internal(
        interpreters=interpreters,
        platforms=platforms,
        requirements=requirements,
        requirement_files=requirement_files,
        constraint_files=constraint_files,
        allow_prereleases=allow_prereleases,
        transitive=transitive,
        indexes=indexes,
        find_links=find_links,
        network_configuration=network_configuration,
        cache=cache,
        build=build,
        use_wheel=use_wheel,
        manylinux=manylinux,
        dest=workspace,
        max_parallel_jobs=max_parallel_jobs,
    )

    install_requests = []
    if download_results is not None:
        for download_result in download_results:
            build_requests.extend(download_result.build_requests())
            install_requests.extend(download_result.install_requests())

    build_and_install_request = BuildAndInstallRequest(
        build_requests=build_requests,
        install_requests=install_requests,
        indexes=indexes,
        find_links=find_links,
        network_configuration=network_configuration,
        cache=cache,
        compile=compile,
    )

    ignore_errors = ignore_errors or not transitive
    return list(
        build_and_install_request.install_distributions(
            ignore_errors=ignore_errors, workspace=workspace, max_parallel_jobs=max_parallel_jobs
        )
    )