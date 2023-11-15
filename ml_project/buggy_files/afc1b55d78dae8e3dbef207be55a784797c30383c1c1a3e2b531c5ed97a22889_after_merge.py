def install(
    local_distributions,
    indexes=None,
    find_links=None,
    network_configuration=None,
    cache=None,
    compile=False,
    max_parallel_jobs=None,
    ignore_errors=False,
):
    """Installs distributions in individual chroots that can be independently added to `sys.path`.

    :keyword local_distributions: The local distributions to install.
    :type local_distributions: list of :class:`LocalDistribution`
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
    :keyword bool compile: Whether to pre-compile resolved distribution python sources.
      Defaults to ``False``.
    :keyword int max_parallel_jobs: The maximum number of parallel jobs to use when resolving,
      building and installing distributions in a resolve. Defaults to the number of CPUs available.
    :keyword bool ignore_errors: Whether to ignore resolution solver errors. Defaults to ``False``.
    :returns: List of :class:`InstalledDistribution` instances meeting ``requirements``.
    :raises Untranslatable: If no compatible distributions could be acquired for
      a particular requirement.
    :raises Unsatisfiable: If not ignoring errors and distribution requirements are found to not be
      transitively satisfiable.
    """

    build_requests = []
    install_requests = []
    for local_distribution in local_distributions:
        if local_distribution.is_wheel:
            install_requests.append(InstallRequest.from_local_distribution(local_distribution))
        else:
            build_requests.append(BuildRequest.from_local_distribution(local_distribution))

    package_index_configuration = PackageIndexConfiguration.create(
        indexes=indexes, find_links=find_links, network_configuration=network_configuration
    )
    build_and_install_request = BuildAndInstallRequest(
        build_requests=build_requests,
        install_requests=install_requests,
        package_index_configuration=package_index_configuration,
        cache=cache,
        compile=compile,
    )

    return list(
        build_and_install_request.install_distributions(
            ignore_errors=ignore_errors, max_parallel_jobs=max_parallel_jobs
        )
    )