def download(
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
    manylinux=None,
    dest=None,
    max_parallel_jobs=None,
):
    """Downloads all distributions needed to meet requirements for multiple distribution targets.

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
    :keyword interpreters: If specified, distributions will be resolved for these interpreters.
      If both `interpreters` and `platforms` are ``None`` (the default) or an empty iterable, this
      defaults to a list containing only the current interpreter.
    :type interpreters: list of :class:`pex.interpreter.PythonInterpreter`
    :keyword platforms: An iterable of PEP425-compatible platform strings to resolve distributions
      for, in addition to the platforms of any given interpreters.
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
    :keyword str manylinux: The upper bound manylinux standard to support when targeting foreign linux
      platforms. Defaults to ``None``.
    :keyword str dest: A directory path to download distributions to.
    :keyword int max_parallel_jobs: The maximum number of parallel jobs to use when resolving,
      building and installing distributions in a resolve. Defaults to the number of CPUs available.
    :returns: List of :class:`LocalDistribution` instances meeting ``requirements``.
    :raises Unsatisfiable: If the resolution of download of distributions fails for any reason.
    :raises ValueError: If a foreign platform was provided in `platforms`, and `use_wheel=False`.
    :raises ValueError: If `build=False` and `use_wheel=False`.
    """

    local_distributions, download_results = _download_internal(
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
        dest=dest,
        max_parallel_jobs=max_parallel_jobs,
    )

    for download_result in download_results:
        for build_request in download_result.build_requests():
            local_distributions.append(
                LocalDistribution(
                    target=build_request.target,
                    path=build_request.source_path,
                    fingerprint=build_request.fingerprint,
                )
            )
        for install_request in download_result.install_requests():
            local_distributions.append(
                LocalDistribution(
                    target=install_request.target,
                    path=install_request.wheel_path,
                    fingerprint=install_request.fingerprint,
                )
            )

    return local_distributions