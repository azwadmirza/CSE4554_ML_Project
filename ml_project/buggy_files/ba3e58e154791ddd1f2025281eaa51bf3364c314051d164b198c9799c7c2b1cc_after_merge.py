    def install_distributions(
        self,
        ignore_errors=False,  # type: bool
        workspace=None,  # type: Optional[str]
        max_parallel_jobs=None,  # type: Optional[int]
    ):
        # type: (...) -> Iterable[InstalledDistribution]
        if not any((self._build_requests, self._install_requests)):
            # Nothing to build or install.
            return ()

        cache = self._cache or workspace or safe_mkdtemp()

        built_wheels_dir = os.path.join(cache, "built_wheels")
        spawn_wheel_build = functools.partial(self._spawn_wheel_build, built_wheels_dir)

        installed_wheels_dir = os.path.join(cache, PexInfo.INSTALL_CACHE)
        spawn_install = functools.partial(self._spawn_install, installed_wheels_dir)

        to_install = list(self._install_requests)
        installations = []  # type: List[InstalledDistribution]

        # 1. Build local projects and sdists.
        if self._build_requests:
            with TRACER.timed(
                "Building distributions for:"
                "\n  {}".format("\n  ".join(map(str, self._build_requests)))
            ):

                build_requests, install_requests = self._categorize_build_requests(
                    build_requests=self._build_requests, dist_root=built_wheels_dir
                )
                to_install.extend(install_requests)

                for build_result in execute_parallel(
                    inputs=build_requests,
                    spawn_func=spawn_wheel_build,
                    error_handler=Raise(Untranslatable),
                    max_jobs=max_parallel_jobs,
                ):
                    to_install.append(build_result.finalize_build())

        # 2. All requirements are now in wheel form: calculate any missing direct requirement
        #    project names from the wheel names.
        with TRACER.timed(
            "Calculating project names for direct requirements:"
            "\n  {}".format("\n  ".join(map(str, self._direct_requirements)))
        ):
            build_requests_by_path = {
                build_request.source_path: build_request for build_request in self._build_requests
            }

            def iter_direct_requirements():
                # type: () -> Iterator[Requirement]
                for requirement in self._direct_requirements:
                    if not isinstance(requirement, LocalProjectRequirement):
                        yield requirement.requirement
                        continue

                    build_request = build_requests_by_path.get(requirement.path)
                    if build_request is None:
                        raise AssertionError(
                            "Failed to compute a project name for {requirement}. No corresponding "
                            "build request was found from amongst:\n{build_requests}".format(
                                requirement=requirement,
                                build_requests="\n".join(
                                    sorted(
                                        "{path} -> {build_request}".format(
                                            path=path, build_request=build_request
                                        )
                                        for path, build_request in build_requests_by_path.items()
                                    )
                                ),
                            )
                        )
                    install_req = build_request.result(built_wheels_dir).finalize_build()
                    yield requirement.as_requirement(dist=install_req.wheel_path)

            direct_requirements_by_key = defaultdict(
                OrderedSet
            )  # type: DefaultDict[str, OrderedSet[Requirement]]
            for direct_requirement in iter_direct_requirements():
                direct_requirements_by_key[direct_requirement.key].add(direct_requirement)

        # 3. Install wheels in individual chroots.

        # Dedup by wheel name; e.g.: only install universal wheels once even though they'll get
        # downloaded / built for each interpreter or platform.
        install_requests_by_wheel_file = (
            OrderedDict()
        )  # type: OrderedDict[str, List[InstallRequest]]
        for install_request in to_install:
            install_requests = install_requests_by_wheel_file.setdefault(
                install_request.wheel_file, []
            )
            install_requests.append(install_request)

        representative_install_requests = [
            requests[0] for requests in install_requests_by_wheel_file.values()
        ]

        def add_installation(install_result):
            install_requests = install_requests_by_wheel_file[install_result.request.wheel_file]
            installations.extend(install_result.finalize_install(install_requests))

        with TRACER.timed(
            "Installing:" "\n  {}".format("\n  ".join(map(str, representative_install_requests)))
        ):
            install_requests, install_results = self._categorize_install_requests(
                install_requests=representative_install_requests,
                installed_wheels_dir=installed_wheels_dir,
            )
            for install_result in install_results:
                add_installation(install_result)

            for install_result in execute_parallel(
                inputs=install_requests,
                spawn_func=spawn_install,
                error_handler=Raise(Untranslatable),
                max_jobs=max_parallel_jobs,
            ):
                add_installation(install_result)

        if not ignore_errors:
            self._check_install(installations)

        installed_distributions = OrderedSet()  # type: OrderedSet[InstalledDistribution]
        for installed_distribution in installations:
            distribution = installed_distribution.distribution
            direct_reqs = [
                req
                for req in direct_requirements_by_key.get(distribution.key, ())
                if req
                and distribution in req
                and installed_distribution.target.requirement_applies(req)
            ]
            if len(direct_reqs) > 1:
                raise AssertionError(
                    "More than one direct requirement is satisfied by {distribution}:\n"
                    "{requirements}\n"
                    "This should never happen since Pip fails when more than one requirement for "
                    "a given project name key is supplied and applies for a given target "
                    "interpreter environment.".format(
                        distribution=distribution,
                        requirements="\n".join(
                            "{index}. {direct_req}".format(index=index, direct_req=direct_req)
                            for index, direct_req in enumerate(direct_reqs)
                        ),
                    )
                )
            installed_distributions.add(
                installed_distribution.with_direct_requirement(
                    direct_requirement=direct_reqs[0] if direct_reqs else None
                )
            )
        return installed_distributions