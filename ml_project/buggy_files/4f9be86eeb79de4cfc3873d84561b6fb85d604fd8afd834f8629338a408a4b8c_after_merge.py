def _download_internal(
    requirements=None,
    requirement_files=None,
    constraint_files=None,
    allow_prereleases=False,
    transitive=True,
    interpreters=None,
    platforms=None,
    package_index_configuration=None,
    cache=None,
    build=True,
    use_wheel=True,
    manylinux=None,
    dest=None,
    max_parallel_jobs=None,
):

    parsed_platforms = [parsed_platform(platform) for platform in platforms] if platforms else []

    def iter_targets():
        if not interpreters and not parsed_platforms:
            # No specified targets, so just build for the current interpreter (on the current platform).
            yield DistributionTarget.current()
            return

        if interpreters:
            for interpreter in interpreters:
                # Build for the specified local interpreters (on the current platform).
                yield DistributionTarget.for_interpreter(interpreter)

        if parsed_platforms:
            for platform in parsed_platforms:
                if platform is not None or not interpreters:
                    # 1. Build for specific platforms.
                    # 2. Build for the current platform (None) only if not done already (ie: no intepreters
                    #    were specified).
                    yield DistributionTarget.for_platform(platform)

    # Only download for each target once. The download code assumes this unique targets optimization
    # when spawning parallel downloads.
    # TODO(John Sirois): centralize the de-deuping in the DownloadRequest constructor when we drop
    # python 2.7 and move from namedtuples to dataclasses.
    unique_targets = OrderedSet(iter_targets())
    download_request = DownloadRequest(
        targets=unique_targets,
        requirements=requirements,
        requirement_files=requirement_files,
        constraint_files=constraint_files,
        allow_prereleases=allow_prereleases,
        transitive=transitive,
        package_index_configuration=package_index_configuration,
        cache=cache,
        build=build,
        use_wheel=use_wheel,
        manylinux=manylinux,
    )

    local_projects = list(download_request.iter_local_projects())

    dest = dest or safe_mkdtemp()
    download_results = download_request.download_distributions(
        dest=dest, max_parallel_jobs=max_parallel_jobs
    )
    return local_projects, download_results